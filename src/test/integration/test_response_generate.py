# SPDX-FileCopyrightText: Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import tempfile
import unittest
from typing import List

import notify2  # pyright: ignore [reportMissingTypeStubs]
from langchain_chroma import Chroma
from langchain_community.chat_models import FakeListChatModel
from langchain_community.embeddings import FakeEmbeddings
from mockito import (  # pyright: ignore [reportMissingTypeStubs]
    unstub,  # pyright: ignore [reportUnknownVariableType]
    when,  # pyright: ignore [reportUnknownVariableType]
)

from chat_script import chain, options, response
from chat_script.chain import Models

# pyright: reportUnknownMemberType=false


class Document:
    metadata = {"source": "def"}
    page_content = "abc"


class Request:
    class Client:
        host = "127.0.0.1"

    client = Client()


class MockLLM:
    def invoke(self, question: str):
        text = "safe"
        return text


class MockLLM_reject:
    def invoke(self, question: str):
        text = "unsafe"
        return text


class Alert:
    def show(self):
        print("Alert triggered")


class SimpleRetriever:
    docs: List[Document]
    k: int = 5


class TestResponseGenerate(unittest.TestCase):
    def test_generate(self):
        def opt(option_name: str):
            """Syntactic sugar for retrieving options"""
            return options.OPTIONS["chain"][option_name]

        mock_mod = MockLLM()
        mock_llm = FakeListChatModel(responses=["a"])
        mock_embed = FakeEmbeddings(size=1024)
        models: Models = {"embeddings_model": mock_embed, "chat_model": mock_llm}  # pyright: ignore [reportAssignmentType]
        request = Request()
        alert = Alert()
        options.read()

        with tempfile.TemporaryDirectory() as EMBED_DIR:
            chain.EMBED_DIR = EMBED_DIR
            vectorstore = Chroma(
                collection_name=str(opt("collection_name")),
                embedding_function=models["embeddings_model"],
                persist_directory=os.path.expanduser(EMBED_DIR),
            )
            mock_retriever = SimpleRetriever()

            when(chain).prepare_models().thenReturn(models)
            when(chain).create_moderation().thenReturn(mock_mod)
            when(notify2).Notification("Unsafe question received").thenReturn(alert)
            when(vectorstore).as_retriever(
                search_kwargs={"k": opt("top_n_results_fusion")}
            ).thenReturn(mock_retriever)
            when(vectorstore).as_retriever(
                search_kwargs={"k": opt("top_n_results")}
            ).thenReturn(mock_retriever)

            chain.create()
            generated = response.generate("", "", request)  # pyright: ignore [reportArgumentType]
            for _index in range(3):
                next(generated)
            unstub()

    def test_generate_unsafe(self):
        def opt(option_name: str):
            """Syntactic sugar for retrieving options"""
            return options.OPTIONS["chain"][option_name]

        mock_mod = MockLLM_reject()
        mock_llm = FakeListChatModel(responses=["a"])
        mock_embed = FakeEmbeddings(size=1024)
        models: Models = {"embeddings_model": mock_embed, "chat_model": mock_llm}  # pyright: ignore [reportAssignmentType]
        request = Request()
        alert = Alert()
        options.read()

        with tempfile.TemporaryDirectory() as EMBED_DIR:
            chain.EMBED_DIR = EMBED_DIR
            vectorstore = Chroma(
                collection_name=str(opt("collection_name")),
                embedding_function=models["embeddings_model"],
                persist_directory=os.path.expanduser(EMBED_DIR),
            )
            mock_retriever = SimpleRetriever()

            when(chain).prepare_models().thenReturn(models)
            when(chain).create_moderation().thenReturn(mock_mod)
            when(notify2).Notification("Unsafe question received").thenReturn(alert)
            when(vectorstore).as_retriever(
                search_kwargs={"k": opt("top_n_results_fusion")}
            ).thenReturn(mock_retriever)
            when(vectorstore).as_retriever(
                search_kwargs={"k": opt("top_n_results")}
            ).thenReturn(mock_retriever)

            chain.create()
            generated = response.generate("", "", request)  # pyright: ignore [reportArgumentType]
            for _index in range(3):
                next(generated)
            unstub()
