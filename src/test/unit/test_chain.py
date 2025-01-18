# SPDX-FileCopyrightText: 2024-2025 Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import tempfile
import unittest
from langchain_core.embeddings.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables.base import Runnable
from chat_script import chain, options


class TestChain(unittest.TestCase):
    def test_opt(self):
        options.read()
        embeddings_gpu = chain.opt("embeddings_gpu")
        self.assertTrue(isinstance(embeddings_gpu, bool))

    def test_prepare_models(self):
        embeddings, model = chain.prepare_models()
        self.assertTrue(isinstance(embeddings, Embeddings))
        self.assertTrue(isinstance(model, BaseChatModel))

    def test_prepare_prompts(self):
        qa_prompt, contextualize_q_prompt = chain.prepare_prompts()
        self.assertTrue(isinstance(qa_prompt, ChatPromptTemplate))
        self.assertTrue(isinstance(contextualize_q_prompt, ChatPromptTemplate))

    def test_create(self):
        if not hasattr(options, "OPTIONS"):
            options.read()
        with tempfile.TemporaryDirectory() as EMBED_DIR:
            chain.EMBED_DIR = EMBED_DIR
            chain.create()
            rag_chain = chain.rag_chain
            self.assertTrue(isinstance(rag_chain, Runnable))

    def test_create_moderation(self):
        if not hasattr(options, "OPTIONS"):
            options.read()
        moderation_chain = chain.create_moderation()
        self.assertTrue(isinstance(moderation_chain, Runnable))
