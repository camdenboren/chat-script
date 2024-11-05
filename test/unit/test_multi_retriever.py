# SPDX-FileCopyrightText: 2024 Camden Boren
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from langchain_core.retrievers import BaseRetriever
from src import multi_retriever


class TestMultiRetriever(unittest.TestCase):
    def test_prepare(self):
        self.assertTrue(issubclass(multi_retriever.prepare(2), BaseRetriever))
