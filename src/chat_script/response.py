# SPDX-FileCopyrightText: Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

"""Returns response w/ citations from RAG-enabled LLM based on user question passed from app ui"""

import os
import platform
import time
from typing import Iterator, cast

import notify2  # pyright: ignore [reportMissingTypeStubs]
from gradio import Request
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.documents.base import Document
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import (
    RunnableWithMessageHistory,
)
from langchain_core.runnables.utils import AddableDict

from chat_script import chain, options

# Directory and file names
SCRIPTS_DIR = "~/.chat-script/scripts"

# Calculate length of scripts_dir name for citation formatting later
SCRIPTS_DIR_LEN = len(os.path.expanduser(SCRIPTS_DIR))
if SCRIPTS_DIR[-1] != "/":
    SCRIPTS_DIR_LEN += 1  # pyright: ignore [reportConstantRedefinition]

# Message sent when unsafe question is asked and options.OPTIONS['response']['moderate'] = True
UNSAFE_RESPONSE = "Your question is unsafe, so no response will be provided."


def opt(option_name: str) -> bool | str | int | float:
    """Syntactic sugar for retrieving options"""
    return options.OPTIONS["response"][option_name]


def check_question(question: str, request: Request) -> bool:
    """Determines whether a response may be generated based on config and user input"""
    host: str = str(request.client.host)  # pyright: ignore [reportUnknownArgumentType, reportUnknownMemberType]
    if request and opt("print_state"):
        print("\nIP address of user: ", host, sep="")
    allow_response = True
    if opt("moderate"):
        moderation_chain = chain.create_moderation()
        moderation_result = moderation_chain.invoke(question)
        allow_response = moderation_result[0:4] == "safe"
    return allow_response


def convert_session_history(history: list[list[str]]) -> None:
    """Workaround for converting Gradio history to Langchain-compatible chat_history."""
    global session_history
    session_history = ChatMessageHistory()

    # Remove unsafe messages from history if applicable
    if opt("moderate"):
        for msgs in history:
            if msgs[1] == f"{UNSAFE_RESPONSE} ":
                history.remove(msgs)

    # Trim history before converting to langchain format
    if len(history) > int(opt("max_history")):
        history = history[-int(opt("max_history")) :]
    for msgs in history:
        session_history.add_user_message(msgs[0])
        session_history.add_ai_message(msgs[1].split("\n\nRelevant Sources")[0])


def get_session_history() -> BaseChatMessageHistory:
    """Manage chat history"""
    return session_history


def inspect(state: AddableDict) -> AddableDict:
    """Print state between runnables and pass it on (includes: input, chat_history)"""
    if opt("print_state"):
        print("State: ", state, sep="")
    return state


def prepare_rag_history() -> RunnableWithMessageHistory:
    """Define retrieval chain w/ history"""
    rag_history_chain = RunnableWithMessageHistory(
        RunnableLambda(inspect) | chain.rag_chain,  # pyright: ignore [reportArgumentType]
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    # Old approach for including context in state -
    # investigate this further to prevent separate context printing
    # retrieve_docs = (lambda x: x["input"]) | retriever
    # chain = RunnablePassthrough.assign(
    #   context=retrieve_docs
    # ).assign(
    #   answer=rag_chain_from_docs
    # )
    return rag_history_chain


def format_context(context: list[Document]) -> Iterator[str]:
    """Formats and yields context passed to LLM in human-readable format"""
    if opt("print_state"):
        print("Context: ", context, sep="")
    formatted_context = "Relevant Sources: "
    yield "\n\n"
    for index, chunk in enumerate(context):
        meta = cast(dict[str, str], chunk.metadata)  # pyright: ignore [reportUnknownMemberType]
        formatted_context += f"[{str(index + 1)}] {meta['source'][SCRIPTS_DIR_LEN:]}"
        for fmt_chunks in formatted_context.split():
            yield f"{fmt_chunks} "
            if (index == 0) and (fmt_chunks == "Sources:"):
                yield "\n"
            time.sleep(float(opt("context_stream_delay")))
        yield "\n"
        formatted_context = ""


def reject(question: str, request: Request) -> None:
    """Display log, alert based on config"""
    if opt("moderate_alert") and platform.system() == "Linux":
        notify2.init("chat-script")  # pyright: ignore [reportUnknownMemberType]
        alert = notify2.Notification("Unsafe question received")
        alert.show()

    host: str = str(request.client.host)  # pyright: ignore [reportUnknownArgumentType, reportUnknownMemberType]
    if request and not opt("print_state"):
        print("\nIP address of user: ", host, sep="")
    print("Unsafe question: '", question, "'", sep="")


def rejection_message() -> Iterator[str]:
    """Yield unsafe response info to user"""
    response_stream: str = ""
    for chunks in UNSAFE_RESPONSE.split():
        response_stream += f"{chunks} "
        yield response_stream
        response_stream = ""
        time.sleep(float(opt("context_stream_delay")))


def generate(
    question: str, history: list[list[str]], request: Request
) -> Iterator[str]:
    """Creates RAG + history chain w/ local LLM and streams chain's text response"""
    if check_question(question, request):
        convert_session_history(history)
        rag_history_chain = prepare_rag_history()

        # Yield response and formatted context (if applicable) as a text stream
        result: Iterator[AddableDict] = rag_history_chain.stream(  # pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
            {"input": question}, config={"configurable": {"session_id": "unused"}}
        )
        response_stream: str = ""
        context: list[Document] | None = None
        for chunks in result:
            answer_chunks = chunks.get("answer")
            get_context: list[Document] | None = cast(
                list[Document] | None, chunks.get("context")
            )
            if answer_chunks:
                response_stream += answer_chunks
            if get_context:
                context: list[Document] | None = get_context
            yield response_stream
        if context:
            formatted_context: Iterator[str] = format_context(context)
            for context_chunks in formatted_context:
                response_stream += context_chunks
                yield response_stream
    else:
        reject(question, request)
        rejection = rejection_message()
        response_stream: str = ""
        for reject_chunks in rejection:
            response_stream += reject_chunks
            yield response_stream
