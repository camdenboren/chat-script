import unittest
from typing import List
from langchain_core.embeddings.embeddings import Embeddings
from src import embeddings, options

class Document:
    metadata = {"source": "def"}
    page_content = "abc"

class TestEmbeddings(unittest.TestCase):
    def test_opt(self):
        options.read()
        show_progress = embeddings.opt('show_progress')
        self.assertTrue(isinstance(show_progress, bool))

    def test_split(self):
        doc = Document()
        docs = [doc]
        all_splits = embeddings.split(docs)
        self.assertTrue(isinstance(next(all_splits), list))

    def test_prepare_model(self):
        embed_model = embeddings.prepare_model()
        self.assertTrue(isinstance(embed_model, Embeddings))
