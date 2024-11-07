# SPDX-FileCopyrightText: 2024 Camden Boren
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import tempfile
import unittest
import time
import io
import sys
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.utils import AddableDict
from langchain_core.runnables.history import RunnableWithMessageHistory
import notify2
from mockito import when, unstub
from src import chain, response, options


class Document:
    metadata = {"source": "def"}
    page_content = "abc"


class Request:
    class Client:
        host = "127.0.0.1"

    client = Client()


class MockLLM:
    def invoke(self):
        text = "abc def"
        return text


class Alert:
    def show(self):
        print("Alert triggered")


class TestResponse(unittest.TestCase):
    def test_opt(self):
        options.read()
        print_state = response.opt("print_state")
        self.assertTrue(isinstance(print_state, bool))

    def test_check_question(self):
        if not hasattr(options, 'OPTIONS'):
            options.read()
        when(chain).create_moderation().thenReturn(MockLLM)
        request = Request()
        allow_response = response.check_question("", request)
        unstub()
        self.assertTrue(isinstance(allow_response, bool))

    def test_convert_session_history(self):
        if not hasattr(options, 'OPTIONS'):
            options.read()
        history = [
            ["how do", "To "],
            ["what if ", "If you onxt "],
            ["what is", " In this "],
        ]

        response.convert_session_history(history)
        session_history = response.session_history
        self.assertTrue(isinstance(session_history, ChatMessageHistory))

    def test_inspect(self):
        if not hasattr(options, 'OPTIONS'):
            options.read()
        empty_state = AddableDict()
        state = response.inspect(empty_state)
        self.assertTrue(isinstance(state, AddableDict))

    def test_get_session_history(self):
        if not hasattr(options, 'OPTIONS'):
            options.read()
        response.convert_session_history("")
        session_history = response.get_session_history()
        self.assertTrue(isinstance(session_history, BaseChatMessageHistory))

    def test_prepare_rag_history(self):
        with tempfile.TemporaryDirectory() as EMBED_DIR:
            chain.EMBED_DIR = EMBED_DIR
            chain.create()
            rag_history_chain = response.prepare_rag_history()
            self.assertTrue(isinstance(rag_history_chain, RunnableWithMessageHistory))

    def test_format_context(self):
        def opt(option_name):
            """Syntactic sugar for retrieving options"""
            if not hasattr(options, 'OPTIONS'):
                options.read()
            return options.OPTIONS["response"][option_name]

        context = [Document]
        formatted = response.format_context(context)
        when(time).sleep(opt("context_stream_delay")).thenReturn(None)
        for index in range(6):
            self.assertTrue(isinstance(next(formatted), str))

    def test_reject(self):
        alert = Alert()
        when(notify2).Notification("Unsafe question received").thenReturn(alert)
        captured_output = io.StringIO()
        sys.stdout = captured_output
        request = Request()
        response.reject("", request)
        sys.stdout = sys.__stdout__
        unstub()
        self.assertTrue(isinstance(captured_output.getvalue(), str))

    def test_rejection_message(self):
        rejection = response.rejection_message()
        self.assertTrue(isinstance(next(rejection), str))
