# SPDX-FileCopyrightText: Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

"""Setup language models and multi-query retriever, define the moderation and rag chains"""

import os
from typing import TypedDict, cast

from langchain.chains.combine_documents import (
    create_stuff_documents_chain,  # pyright: ignore [reportUnknownVariableType]
)
from langchain.chains.history_aware_retriever import (
    create_history_aware_retriever,  # pyright: ignore [reportUnknownVariableType]
)
from langchain.chains.retrieval import (
    create_retrieval_chain,  # pyright: ignore [reportUnknownVariableType]
)
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.language_models import LanguageModelInput, LanguageModelLike
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable, RunnableSerializable
from langchain_ollama import ChatOllama

from chat_script import multi_retriever, options

# Directory and file names
EMBED_DIR = "~/.chat-script/embeddings"


class Models(TypedDict):
    """Representation of the models used in the application"""

    embeddings_model: OllamaEmbeddings
    chat_model: ChatOllama


def opt(option_name: str) -> bool | str | int | float:
    """Syntactic sugar for retrieving options"""
    return options.OPTIONS["chain"][option_name]


def prepare_models() -> Models:
    """Set num_gpu depending on whether opt('embeddings_gpu') is True or False"""
    if opt("embeddings_gpu"):
        num_gpu = None
    else:
        num_gpu = 0

    # Set Embedding LLM to local Ollama model
    embeddings = OllamaEmbeddings(
        model=str(opt("embeddings_model")),
        base_url=str(opt("embeddings_url")),
        show_progress=bool(opt("show_progress")),
        num_gpu=num_gpu,
    )

    # Set LLM to local Ollama model
    model = ChatOllama(
        model=str(opt("chat_model")),
        keep_alive=str(opt("keep_alive")),
        base_url=str(opt("chat_url")),
        temperature=float(opt("temperature")),
        top_k=int(opt("top_k")),
        top_p=float(opt("top_p")),
    )

    return {"embeddings_model": embeddings, "chat_model": model}


def prepare_prompts() -> tuple[ChatPromptTemplate, ChatPromptTemplate]:
    """Define the contextualization prompt for summarizing chat history"""
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages(  # pyright: ignore [reportUnknownMemberType]
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    # Define the question_answer_chain
    system_prompt = "Answer the question using the following context: {context}"
    qa_prompt = ChatPromptTemplate.from_messages(  # pyright: ignore [reportUnknownMemberType]
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    return qa_prompt, contextualize_q_prompt


def create() -> None:
    """Set ChromaDB vectorstore (w/ opt('collection_name')) as a retriever and create rag_chain"""
    models = prepare_models()
    qa_prompt, contextualize_q_prompt = prepare_prompts()

    vectorstore = Chroma(
        collection_name=str(opt("collection_name")),
        embedding_function=models["embeddings_model"],
        persist_directory=os.path.expanduser(EMBED_DIR),
    )

    if opt("rag_fusion"):
        MultiQueryRetriever = multi_retriever.prepare(int(opt("num_queries")))
        retriever_fusion = MultiQueryRetriever.from_llm(
            retriever=vectorstore.as_retriever(
                search_kwargs={"k": opt("top_n_results_fusion")}
            ),
            llm=models["chat_model"],
            include_original=True,
        )
        retriever = create_history_aware_retriever(
            models["chat_model"],
            retriever_fusion,
            contextualize_q_prompt,
        )
    else:
        retriever = create_history_aware_retriever(
            models["chat_model"],
            vectorstore.as_retriever(search_kwargs={"k": opt("top_n_results")}),
            contextualize_q_prompt,
        )

    global rag_chain
    question_answer_chain = create_stuff_documents_chain(
        models["chat_model"], qa_prompt
    )
    rag_chain = cast(
        Runnable[dict[str, str], LanguageModelLike],
        create_retrieval_chain(retriever, question_answer_chain),
    )


def create_moderation() -> RunnableSerializable[LanguageModelInput, str]:
    """Set Moderation LLM to local Ollama model, construct and return chain"""
    moderation = ChatOllama(
        model=str(opt("moderation_model")),
        keep_alive=str(opt("keep_alive")),
        base_url=str(opt("moderation_url")),
    )
    moderation_chain = moderation | StrOutputParser()
    return moderation_chain
