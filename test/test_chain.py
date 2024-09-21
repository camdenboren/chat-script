import unittest
from langchain_core.embeddings.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts.chat import ChatPromptTemplate
from src import chain, options

class TestChain(unittest.TestCase):
    def test_opt(self):
        options.read()
        embeddings_gpu = chain.opt('embeddings_gpu')
        self.assertTrue(isinstance(embeddings_gpu, bool))

    def test_prepare_models(self):
        embeddings, model = chain.prepare_models()
        self.assertTrue(isinstance(embeddings, Embeddings))
        self.assertTrue(isinstance(model, BaseChatModel))

    def test_prepare_prompts(self):
        qa_prompt, contextualize_q_prompt = chain.prepare_prompts()
        self.assertTrue(isinstance(qa_prompt, ChatPromptTemplate))
        self.assertTrue(isinstance(contextualize_q_prompt, ChatPromptTemplate))
