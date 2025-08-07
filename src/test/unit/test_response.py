# SPDX-FileCopyrightText: Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

import io
import sys
import tempfile
import time
import unittest

import notify2  # pyright: ignore [reportMissingTypeStubs]
from langchain_core.runnables.utils import AddableDict
from mockito import (  # pyright: ignore [reportMissingTypeStubs]
    unstub,  # pyright: ignore [reportUnknownVariableType]
    when,  # pyright: ignore [reportUnknownVariableType]
)

from chat_script import chain, options, response

# pyright: reportUnknownMemberType=false


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
        if not hasattr(options, "OPTIONS"):
            options.read()
        when(chain).create_moderation().thenReturn(MockLLM)
        request = Request()
        _allow_response = response.check_question("", request)  # pyright: ignore [reportArgumentType]
        unstub()

    def test_convert_session_history(self):
        if not hasattr(options, "OPTIONS"):
            options.read()
        history = [
            ["how do", "To "],
            ["what if ", "If you onxt "],
            ["what is", " In this "],
        ]

        response.convert_session_history(history)
        _session_history = response.session_history

    def test_inspect(self):
        if not hasattr(options, "OPTIONS"):
            options.read()
        empty_state = AddableDict()
        _state = response.inspect(empty_state)

    def test_get_session_history(self):
        if not hasattr(options, "OPTIONS"):
            options.read()
        response.convert_session_history([["", ""]])
        _session_history = response.get_session_history()

    def test_prepare_rag_history(self):
        with tempfile.TemporaryDirectory() as EMBED_DIR:
            chain.EMBED_DIR = EMBED_DIR
            chain.create()
            _rag_history_chain = response.prepare_rag_history()

    def test_format_context(self):
        def opt(option_name: str):
            """Syntactic sugar for retrieving options"""
            if not hasattr(options, "OPTIONS"):
                options.read()
            return options.OPTIONS["response"][option_name]

        context = [Document]
        formatted = response.format_context(context)  # pyright: ignore [reportArgumentType]
        when(time).sleep(opt("context_stream_delay")).thenReturn(None)
        for _index in range(6):
            next(formatted)

    def test_reject(self):
        alert = Alert()
        when(notify2).Notification("Unsafe question received").thenReturn(alert)
        captured_output = io.StringIO()
        sys.stdout = captured_output
        request = Request()
        response.reject("", request)  # pyright: ignore [reportArgumentType]
        sys.stdout = sys.__stdout__
        unstub()

    def test_rejection_message(self):
        rejection = response.rejection_message()
        next(rejection)
