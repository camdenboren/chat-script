# SPDX-FileCopyrightText: 2024-2025 Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import tempfile
import unittest
from typing import List

import notify2
from langchain_chroma import Chroma
from langchain_community.chat_models import FakeListChatModel
from langchain_community.embeddings import FakeEmbeddings
from mockito import unstub, when

from chat_script import chain, options, response


class Document:
    metadata = {"source": "def"}
    page_content = "abc"


class Request:
    class Client:
        host = "127.0.0.1"

    client = Client()


class MockLLM:
    def invoke(self, question):
        text = "safe"
        return text


class MockLLM_reject:
    def invoke(self, question):
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
        def opt(option_name):
            """Syntactic sugar for retrieving options"""
            return options.OPTIONS["chain"][option_name]

        mock_mod = MockLLM()
        mock_llm = FakeListChatModel(responses=["a"])
        mock_embed = FakeEmbeddings(size=1024)
        models = [mock_embed, mock_llm]
        request = Request()
        alert = Alert()
        options.read()

        with tempfile.TemporaryDirectory() as EMBED_DIR:
            chain.EMBED_DIR = EMBED_DIR
            vectorstore = Chroma(
                collection_name=opt("collection_name"),
                embedding_function=models[0],
                persist_directory=os.path.expanduser(EMBED_DIR),
            )
            mock_retriever = SimpleRetriever()

            when(chain).prepare_models().thenReturn([mock_embed, mock_llm])
            when(chain).create_moderation().thenReturn(mock_mod)
            when(notify2).Notification("Unsafe question received").thenReturn(alert)
            when(vectorstore).as_retriever(
                search_kwargs={"k": opt("top_n_results_fusion")}
            ).thenReturn(mock_retriever)
            when(vectorstore).as_retriever(
                search_kwargs={"k": opt("top_n_results")}
            ).thenReturn(mock_retriever)

            chain.create()
            generated = response.generate("", "", request)  # pyright: ignore
            for index in range(3):
                self.assertTrue(isinstance(next(generated), str))
            unstub()

    def test_generate_unsafe(self):
        def opt(option_name):
            """Syntactic sugar for retrieving options"""
            return options.OPTIONS["chain"][option_name]

        mock_mod = MockLLM_reject()
        mock_llm = FakeListChatModel(responses=["a"])
        mock_embed = FakeEmbeddings(size=1024)
        models = [mock_embed, mock_llm]
        request = Request()
        alert = Alert()
        options.read()

        with tempfile.TemporaryDirectory() as EMBED_DIR:
            chain.EMBED_DIR = EMBED_DIR
            vectorstore = Chroma(
                collection_name=opt("collection_name"),
                embedding_function=models[0],
                persist_directory=os.path.expanduser(EMBED_DIR),
            )
            mock_retriever = SimpleRetriever()

            when(chain).prepare_models().thenReturn([mock_embed, mock_llm])
            when(chain).create_moderation().thenReturn(mock_mod)
            when(notify2).Notification("Unsafe question received").thenReturn(alert)
            when(vectorstore).as_retriever(
                search_kwargs={"k": opt("top_n_results_fusion")}
            ).thenReturn(mock_retriever)
            when(vectorstore).as_retriever(
                search_kwargs={"k": opt("top_n_results")}
            ).thenReturn(mock_retriever)

            chain.create()
            generated = response.generate("", "", request)  # pyright: ignore
            for index in range(3):
                self.assertTrue(isinstance(next(generated), str))
            unstub()
