# SPDX-FileCopyrightText: Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

import tempfile
import unittest

from chat_script import chain, options


class TestChain(unittest.TestCase):
    def test_opt(self):
        options.read()
        embeddings_gpu = chain.opt("embeddings_gpu")
        self.assertTrue(isinstance(embeddings_gpu, bool))

    def test_prepare_models(self):
        _models = chain.prepare_models()

    def test_prepare_prompts(self):
        _qa_prompt, _contextualize_q_prompt = chain.prepare_prompts()

    def test_create(self):
        if not hasattr(options, "OPTIONS"):
            options.read()
        with tempfile.TemporaryDirectory() as EMBED_DIR:
            chain.EMBED_DIR = EMBED_DIR
            chain.create()

    def test_create_moderation(self):
        if not hasattr(options, "OPTIONS"):
            options.read()
        _moderation_chain = chain.create_moderation()
