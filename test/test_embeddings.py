import unittest
from src import embeddings, options

class TestEmbeddings(unittest.TestCase):
    def test_opt(self):
        options.read()
        show_progress = embeddings.opt('show_progress')
        self.assertTrue(isinstance(show_progress, bool))
