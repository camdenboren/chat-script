# SPDX-FileCopyrightText: Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import tempfile
import unittest

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from mockito import (  # pyright: ignore [reportMissingTypeStubs]
    unstub,  # pyright: ignore [reportUnknownVariableType]
    when,  # pyright: ignore [reportUnknownVariableType]
)

from chat_script import embeddings, options


class Document:
    metadata = {"source": "def"}
    page_content = "abc"


class TestEmbeddings(unittest.TestCase):
    def test_opt(self):
        options.read()
        show_progress = embeddings.opt("show_progress")
        self.assertTrue(isinstance(show_progress, bool))

    def test_load(self):
        def opt(option_name: str):
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
                show_progress=bool(opt("show_progress")),
                use_multithreading=bool(opt("use_multithreading")),
            )

            embeddings.SCRIPTS_DIR = SCRIPTS_DIR

            when(loader).load(
                # pyright: ignore [reportUnknownMemberType]
            ).thenReturn(docs)
            _docs_return = embeddings.load()
            unstub()

    def test_split(self):
        doc = Document()
        docs = [doc]
        _all_splits = embeddings.split(docs)  # pyright: ignore [reportArgumentType]

    def test_prepare_model(self):
        _embed_model = embeddings.prepare_model()
