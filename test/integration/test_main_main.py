import os
import tempfile
import unittest
from mockito import when, unstub
from src import __main__, app, options


class TestMainMain(unittest.TestCase):
    def test_main_branch_one(self):
        with tempfile.TemporaryDirectory() as CONFIG_DIR:
            real_dir = __main__.CONFIG_DIR
            __main__.CONFIG_DIR = CONFIG_DIR
            __main__.CONFIG_FILE = f"{CONFIG_DIR}/chat-script.ini"

            with tempfile.TemporaryDirectory() as SCRIPTS_DIR:
                __main__.SCRIPTS_DIR = SCRIPTS_DIR

                when(app).launch().thenReturn()
                when(options).create().thenReturn()
                __main__.main()
                unstub()

            __main__.CONFIG_DIR = real_dir
            __main__.CONFIG_FILE = f"{CONFIG_DIR}/chat-script.ini"
