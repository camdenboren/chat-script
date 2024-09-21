import unittest
from src import response, options

class TestResponse(unittest.TestCase):
    def test_opt(self):
        options.read()
        print_state = response.opt('print_state')
        self.assertTrue(isinstance(print_state, bool))
