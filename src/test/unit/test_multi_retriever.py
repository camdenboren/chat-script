# SPDX-FileCopyrightText: Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from chat_script import multi_retriever


class TestMultiRetriever(unittest.TestCase):
    def test_prepare(self):
        multi_retriever.prepare(2)
