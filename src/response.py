"""Returns response w/ citations from RAG-enabled LLM based on user question passed from app ui"""

import os
import time
import platform
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from gradio import Request
import notify2
from src import chain, options

# Directory and file names
SCRIPTS_DIR = "~/.chat-script/scripts"

# Calculate length of scripts_dir name for citation formatting later
SCRIPTS_DIR_LEN = len(os.path.expanduser(SCRIPTS_DIR))
if SCRIPTS_DIR[-1] != "/":
    SCRIPTS_DIR_LEN += 1

# Message sent when unsafe question is asked and options.OPTIONS['response']['moderate'] = True
UNSAFE_RESPONSE = "Your question is unsafe, so no response will be provided."

def opt(option_name):
    """Syntactic sugar for retrieving options"""
    return options.OPTIONS['response'][option_name]

def check_question(question, request):
    """Determines whether a response may be generated based on config and user input"""
    if request and opt('print_state'):
        print("\nIP address of user: ", request.client.host, sep="")
    allow_response = True
    if opt('moderate'):
        moderation_chain = chain.create_moderation()
        moderation_result = moderation_chain.invoke(question)
        allow_response = moderation_result[2:6] == "safe"
    return allow_response

def convert_session_history(history):
    """Workaround for converting Gradio history to Langchain-compatible chat_history."""
    global session_history
    session_history = ChatMessageHistory()

    # Remove unsafe messages from history if applicable
    if opt('moderate'):
        for msgs in history:
            if msgs[1] == f"{UNSAFE_RESPONSE} ":
                history.remove(msgs)

    # Trim history before converting to langchain format
    if len(history) > opt('max_history'):
        history = history[-int(opt('max_history')):]
    for msgs in history:
        session_history.add_user_message(msgs[0])
        session_history.add_ai_message(msgs[1].split("\n\nRelevant Sources")[0])

def get_session_history() -> BaseChatMessageHistory:
    """Manage chat history"""
    return session_history

def inspect(state):
    """Print state between runnables and pass it on (includes: input, chat_history)"""
    if opt('print_state'):
        print("State: ", state, sep="")
    return state

def prepare_rag_history() -> RunnableWithMessageHistory:
    """Define retrieval chain w/ history"""
    rag_history_chain = RunnableWithMessageHistory(
        RunnableLambda(inspect) | chain.rag_chain,
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

def format_context(context):
    """Formats and yields context passed to LLM in human-readable format"""
    if opt('print_state'):
        print("Context: ", context, sep="")
    formatted_context = "Relevant Sources (some may not have been used): "
    yield "\n\n"
    for index, chunk in enumerate(context):
        formatted_context += f"[{str(index+1)}] {chunk.metadata['source'][SCRIPTS_DIR_LEN:]}"
        for fmt_chunks in formatted_context.split():
            yield f"{fmt_chunks} "
            if (index == 0) and (fmt_chunks == "used):"):
                yield "\n"
            time.sleep(opt('context_stream_delay'))
        yield "\n"
        formatted_context = ""

def reject(question, request):
    """Display log, alert based on config"""
    if opt('moderate_alert') and platform.system() == "Linux":
        notify2.init("chat-script")
        alert = notify2.Notification("Unsafe question received")
        alert.show()
    if request and not opt('print_state'):
        print("\nIP address of user: ", request.client.host, sep="")
    print("Unsafe question: \'", question, "\'", sep="")

def rejection_message():
    """Yield unsafe response info to user"""
    response_stream = ""
    for chunks in UNSAFE_RESPONSE.split():
        response_stream += f"{chunks} "
        yield response_stream
        response_stream = ""
        time.sleep(opt('context_stream_delay'))

def generate(question,history,request: Request):
    """Creates RAG + history chain w/ local LLM and streams chain's text response"""
    if check_question(question, request):
        convert_session_history(history)
        rag_history_chain = prepare_rag_history()

        # Yield response and formatted context (if applicable) as a text stream
        result = rag_history_chain.stream(
            {"input": question},
            config={"configurable": {"session_id": "unused"}}
        )
        response_stream = ""
        context = None
        for chunks in result:
            answer_chunks = chunks.get("answer")
            get_context = chunks.get("context")
            if answer_chunks:
                response_stream += answer_chunks
            if get_context:
                context = get_context
            yield response_stream
        if context:
            formatted_context = format_context(context)
            for context_chunks in formatted_context:
                response_stream += context_chunks
                yield response_stream
    else:
        reject(question, request)
        rejection = rejection_message()
        response_stream = ""
        for reject_chunks in rejection:
            response_stream += reject_chunks
            yield response_stream
