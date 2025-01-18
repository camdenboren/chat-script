# SPDX-FileCopyrightText: 2024-2025 Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import tempfile
import unittest
from mockito import when, unstub, matchers
from chat_script import __main__, app, options, embeddings


class TestMainMain(unittest.TestCase):
    def test_main_branch_one_one(self):
        with tempfile.TemporaryDirectory() as CONFIG_DIR:
            real_dir = __main__.CONFIG_DIR
            __main__.CONFIG_DIR = CONFIG_DIR
            __main__.CONFIG_FILE = f"{CONFIG_DIR}/chat-script.ini"

            with tempfile.TemporaryDirectory() as SCRIPTS_DIR:
                real_dir_scr = __main__.SCRIPTS_DIR
                __main__.SCRIPTS_DIR = SCRIPTS_DIR

                when(app).launch().thenReturn()
                when(options).create().thenReturn()
                __main__.main()
                unstub()

            __main__.SCRIPTS_DIR = real_dir_scr
            __main__.CONFIG_DIR = real_dir
            __main__.CONFIG_FILE = f"{CONFIG_DIR}/chat-script.ini"

    def test_main_branch_one_two(self):
        when(os.path).exists(matchers.any).thenReturn(False)
        when(os).makedirs(matchers.any).thenReturn()

        when(app).launch().thenReturn()
        when(options).create().thenReturn()
        __main__.main()
        unstub()

    def test_main_branch_three(self):
        when(os.path).exists(matchers.any).thenReturn(True)
        when(os).makedirs(matchers.any).thenReturn()
        when(app).launch().thenReturn()
        when(embeddings).generate().thenReturn()
        when(options).create().thenReturn()

        __main__.main()
        unstub()
