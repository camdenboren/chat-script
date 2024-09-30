import unittest
import io
import sys
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.utils import AddableDict
from langchain_core.runnables.history import RunnableWithMessageHistory
from src import chain, response, options

class Document:
    metadata = {"source": "def"}
    page_content = "abc"

class Request:
    class Client:
        host = "127.0.0.1"
    client = Client()

class TestResponse(unittest.TestCase):
    def test_opt(self):
        options.read()
        print_state = response.opt('print_state')
        self.assertTrue(isinstance(print_state, bool))

    def test_check_question(self):
        request = Request()
        allow_response = response.check_question("", request)
        self.assertTrue(isinstance(allow_response, bool))

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
        context = [Document]
        formatted = response.format_context(context)
        self.assertTrue(isinstance(next(formatted), str))
        self.assertTrue(isinstance(next(formatted), str))
        self.assertTrue(isinstance(next(formatted), str))

    def test_reject(self):
        captured_output = io.StringIO()
        sys.stdout = captured_output
        response.reject("", Request())
        sys.stdout = sys.__stdout__
        self.assertTrue(isinstance(captured_output.getvalue(), str))

    def test_rejection_message(self):
        rejection = response.rejection_message()
        self.assertTrue(isinstance(next(rejection), str))
