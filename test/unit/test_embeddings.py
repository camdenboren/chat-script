# SPDX-FileCopyrightText: 2024 Camden Boren
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import tempfile
import unittest
from langchain_core.embeddings.embeddings import Embeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from mockito import when, unstub
from src import embeddings, options


class Document:
    metadata = {"source": "def"}
    page_content = "abc"


class TestEmbeddings(unittest.TestCase):
    def test_opt(self):
        options.read()
        show_progress = embeddings.opt("show_progress")
        self.assertTrue(isinstance(show_progress, bool))

    def test_load(self):
        def opt(option_name):
            """Syntactic sugar for retrieving options"""
            if not hasattr(options, "OPTIONS"):
                options.read()
            return options.OPTIONS["embeddings"][option_name]

        with tempfile.TemporaryDirectory() as SCRIPTS_DIR:
            doc = Document()
            docs = [doc]
            loader = DirectoryLoader(
                path=os.path.expanduser(SCRIPTS_DIR),
                loader_cls=TextLoader,
                show_progress=opt("show_progress"),
                use_multithreading=opt("use_multithreading"),
            )

            embeddings.SCRIPTS_DIR = SCRIPTS_DIR

            when(loader).load().thenReturn(docs)
            docs_return = embeddings.load()
            unstub()
            self.assertTrue(isinstance(docs_return, list))

    def test_split(self):
        doc = Document()
        docs = [doc]
        all_splits = embeddings.split(docs)
        self.assertTrue(isinstance(next(all_splits), list))

    def test_prepare_model(self):
        embed_model = embeddings.prepare_model()
        self.assertTrue(isinstance(embed_model, Embeddings))
