# SPDX-FileCopyrightText: Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import tempfile
import unittest

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.embeddings import FakeEmbeddings
from mockito import (  # pyright: ignore [reportMissingTypeStubs]
    unstub,  # pyright: ignore [reportUnknownVariableType]
    when,  # pyright: ignore [reportUnknownVariableType]
)

from chat_script import embeddings, options


class Document:
    metadata = {"source": "def"}
    page_content = "abc"


class TestEmbeddingsGenerate(unittest.TestCase):
    def test_generate(self):
        def opt(option_name: str):
            """Syntactic sugar for retrieving options"""
            return options.OPTIONS["embeddings"][option_name]

        mock_embed = FakeEmbeddings(size=1024)
        options.read()

        with tempfile.TemporaryDirectory() as SCRIPTS_DIR:
            embeddings.EMBED_DIR = SCRIPTS_DIR
            embeddings.SCRIPTS_DIR = SCRIPTS_DIR

            doc = Document()
            docs = [doc]
            loader = DirectoryLoader(
                path=os.path.expanduser(SCRIPTS_DIR),
                loader_cls=TextLoader,
                show_progress=bool(opt("show_progress")),
                use_multithreading=bool(opt("use_multithreading")),
            )

            when(loader).load(
                # pyright: ignore [reportUnknownMemberType]
            ).thenReturn(docs)
            when(embeddings).prepare_model(
                # pyright: ignore [reportUnknownMemberType]
            ).thenReturn(mock_embed)

            embeddings.generate()
            unstub()
