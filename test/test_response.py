import unittest
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.utils import AddableDict
from langchain_core.runnables.history import RunnableWithMessageHistory
from src import chain, response, options

class TestResponse(unittest.TestCase):
    def test_opt(self):
        options.read()
        print_state = response.opt('print_state')
        self.assertTrue(isinstance(print_state, bool))

    def test_convert_session_history(self):
        response.convert_session_history("")
        session_history = response.session_history
        self.assertTrue(isinstance(session_history, ChatMessageHistory))

    def test_inspect(self):
        empty_state = AddableDict()
        state = response.inspect(empty_state)
        self.assertTrue(isinstance(state, AddableDict))

    def test_get_session_history(self):
        response.convert_session_history("")
        session_history = response.get_session_history()
        self.assertTrue(isinstance(session_history, BaseChatMessageHistory))

    def test_prepare_rag_history(self):
        chain.create()
        rag_history_chain = response.prepare_rag_history()
        self.assertTrue(isinstance(rag_history_chain, RunnableWithMessageHistory))

    def test_format_context(self):
        empty_context = []
        formatted = response.format_context(empty_context)
        self.assertTrue(isinstance(next(formatted), str))
