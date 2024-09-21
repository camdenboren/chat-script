import unittest
from src import app

class TestApp(unittest.TestCase):
    def test_opt(self):
        self.assertIn(True or False, opt('share'))