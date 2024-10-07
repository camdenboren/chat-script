import unittest
from src import app, options

class TestApp(unittest.TestCase):
    def test_opt(self):
        options.read()
        share = app.opt('share')
        self.assertTrue(isinstance(share, bool))
