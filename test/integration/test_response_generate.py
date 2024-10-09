import os
import unittest
from typing import List
from mockito import when, unstub
import notify2
from langchain_community.chat_models import FakeListChatModel
from langchain_community.embeddings import FakeEmbeddings
from langchain_chroma import Chroma
from src import response, chain, options

EMBED_DIR = "~/.chat-script/embeddings"

class Document:
    metadata = {"source": "def"}
    page_content = "abc"

class Request:
    class Client:
        host = "127.0.0.1"
    client = Client()

class MockLLM:
    def stream(self, input, config):
        text = "safe"
        for chunks in text:
            yield chunks

    def invoke(self, question):
        text = "\n\nsafe"
        return text

class Alert:
    def show(self):
        print("Alert triggered")

class SimpleRetriever():
    docs: List[Document]
    k: int = 5

    def _get_relevant_documents(self, query: str) -> List[Document]:
        """Return the first k documents from the list of documents"""
        return self.docs[:self.k]

    async def _aget_relevant_documents(self, query: str) -> List[Document]:
        """(Optional) async native implementation."""
        return self.docs[:self.k]

class TestResponseGenerate(unittest.TestCase):
    def test_generate(self):
        def opt(option_name):
            """Syntactic sugar for retrieving options"""
            return options.OPTIONS['chain'][option_name]

        mock_mod = MockLLM()
        mock_llm = FakeListChatModel(responses=['a'])
        mock_embed = FakeEmbeddings(size=1024)
        models = [mock_embed, mock_llm]
        request = Request()
        alert = Alert()
        options.read()
        
        vectorstore = Chroma(
            collection_name=opt('collection_name'),
            embedding_function=models[0],
            persist_directory=os.path.expanduser(EMBED_DIR)
        )
        mock_retriever = SimpleRetriever()

        when(chain).prepare_models().thenReturn([mock_embed, mock_llm])
        when(chain).create_moderation().thenReturn(mock_mod)
        when(notify2).Notification("Unsafe question received").thenReturn(alert)
        when(vectorstore).as_retriever(
            search_kwargs={'k': opt('top_n_results_fusion')}
        ).thenReturn(mock_retriever)
        when(vectorstore).as_retriever(
            search_kwargs={'k': opt('top_n_results')}
        ).thenReturn(mock_retriever)

        chain.create()
        generated = response.generate("", "", request)
        for index in range(3):
            self.assertTrue(isinstance(next(generated), str))
        unstub()
