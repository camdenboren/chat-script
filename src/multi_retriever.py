"""Define and return the rag-fusion retirever and output parser"""

# SPDX-FileCopyrightText: 2024 Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import List
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.language_models import BaseLanguageModel
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.prompts import BasePromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import Runnable
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate


def prepare(num_queries):
    """Define output parser and MultiQueryRetriever"""

    # Define the output parser for rag-fusion. Adapted from multi_query.py
    class LineListOutputParser(BaseOutputParser[List[str]]):
        """Output parser for a list of lines."""

        def parse(self, text: str) -> List[str]:
            lines = text.strip().split("\n")
            return lines

    # Set the rag-fusion prompt, enabling customization
    # of number of queries. Adapted from multi_query.py
    default_query_prompt = PromptTemplate(
        input_variables=["question"],
        template="""You are an AI language model assistant. Your task is 
        to generate """
        + str(num_queries - 1)
        + """ different versions of the given user 
        question to retrieve relevant documents from a vector  database. 
        By generating multiple perspectives on the user question, 
        your goal is to help the user overcome some of the limitations 
        of distance-based similarity search. Provide these alternative 
        questions separated by newlines. Original question: {question}""",
    )

    # Define the retriever for rag-fusion. Adapted from multi_query.py
    class MultiQueryRetriever(BaseRetriever):
        """Given a query, use an LLM to write several and retrieve unique docs."""

        retriever: BaseRetriever
        llm_chain: Runnable
        verbose: bool = True
        parser_key: str = "lines"
        include_original: bool = False

        @classmethod
        def from_llm(
            cls,
            retriever: BaseRetriever,
            llm: BaseLanguageModel,
            prompt: BasePromptTemplate = default_query_prompt,
            include_original: bool = False,
        ) -> "MultiQueryRetriever":
            """Initialize from llm using default template."""
            output_parser = LineListOutputParser()
            llm_chain = prompt | llm | output_parser
            return cls(
                retriever=retriever,
                llm_chain=llm_chain,
                include_original=include_original,
            )

        def _get_relevant_documents(
            self, query: str, *, run_manager: CallbackManagerForRetrieverRun
        ) -> List[Document]:
            """Get relevant docs from multiple derived queries"""
            # Generate queries
            response = self.llm_chain.invoke(
                {"question": query}, config={"callbacks": run_manager.get_child()}
            )
            if isinstance(self.llm_chain, LLMChain):
                lines = response["text"]
            else:
                lines = response
            queries = lines[: max(num_queries - 1, 0)]
            if self.include_original:
                queries.append(query)

            # Retrieve and combine documents for each query
            documents = []
            for query in queries:
                docs = self.retriever.invoke(
                    query, config={"callbacks": run_manager.get_child()}
                )
                documents.extend(docs)

            # Return unique union of retrieved documents
            return [doc for i, doc in enumerate(documents) if doc not in documents[:i]]

    return MultiQueryRetriever
