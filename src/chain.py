# Setup language models and multi-query retriever, define the moderation and rag chains

import os
from typing import List, Optional, Sequence
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.language_models import BaseLanguageModel
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.prompts import BasePromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import Runnable
from langchain.chains.llm import LLMChain
from langchain_core.output_parsers import StrOutputParser
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_community.vectorstores import Chroma
import options

# Directory and file names
embeddings_directory = "~/.chat-script/embeddings"

def prepare_models():
    # Set num_gpu depending on whether options.options['chain']['embeddings_gpu'] is True or False
    global num_gpu
    if options.options['chain']['embeddings_gpu']:
        num_gpu = None
    else:
        num_gpu = 0

    # Set Embedding LLM to local Ollama model
    global embeddings
    embeddings = OllamaEmbeddings(
        model=options.options['chain']['embeddings_model'], 
        show_progress=options.options['chain']['show_progress'], 
        num_gpu=num_gpu
    )

    # Set LLM to local Ollama model
    global model
    model = ChatOllama(
        model=options.options['chain']['chat_model'],
        progress=options.options['chain']['show_progress'],
        keep_alive=options.options['chain']['keep_alive'],
        base_url=options.options['chain']['chat_url'],
        temperature=options.options['chain']['temperature'],
        top_k=options.options['chain']['top_k'],
        top_p=options.options['chain']['top_p']
    )

    # Set Moderation LLM to local Ollama model
    if options.options['chain']['moderate']:
        moderation = ChatOllama(
            model=options.options['chain']['moderation_model'],
            show_progress=options.options['chain']['show_progress'],
            keep_alive=options.options['chain']['keep_alive'],
            base_url=options.options['chain']['moderation_url']
        )
        global moderation_chain
        moderation_chain = moderation | StrOutputParser()

def prepare_prompts():
    # Define the contextualization prompt for summarizing chat history
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )
    global contextualize_q_prompt
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),    
    ])

    # Define the question_answer_chain 
    system_prompt = (
        "Answer the question using the following context. If you use any information in the context, include the index like: [1] of the relevant Document as an in-text citation in your answer, and nothing else. Remember that each Document has two sections: page_content, and metadata- don't confuse these for indexable objects."
        "{context}"
    )
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    global question_answer_chain
    question_answer_chain = create_stuff_documents_chain(model, qa_prompt)

    # Define the output parser for rag-fusion. Adapted from multi_query.py
    class LineListOutputParser(BaseOutputParser[List[str]]):
        """Output parser for a list of lines."""
        def parse(self, text: str) -> List[str]:
            lines = text.strip().split("\n")
            return lines
    # Set the rag-fusion prompt, enabling customization of number of queries. Adapted from multi_query.py
    DEFAULT_QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""You are an AI language model assistant. Your task is 
        to generate """ + str(options.options['chain']['num_queries']-1) + """ different versions of the given user 
        question to retrieve relevant documents from a vector  database. 
        By generating multiple perspectives on the user question, 
        your goal is to help the user overcome some of the limitations 
        of distance-based similarity search. Provide these alternative 
        questions separated by newlines. Original question: {question}""",
    )

    # Define the retriever for rag-fusion. Adapted from multi_query.py
    global MultiQueryRetriever
    class MultiQueryRetriever(BaseRetriever):
        """Given a query, use an LLM to write a set of queries. Retrieve docs for each query. Return the unique union of all retrieved docs."""
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
            prompt: BasePromptTemplate = DEFAULT_QUERY_PROMPT,
            parser_key: Optional[str] = None,
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

        def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> List[Document]:
            """Get relevant and unique documents from multiple derived queries given a single user query."""
            # Generate queries
            response = self.llm_chain.invoke({"question": query}, config={"callbacks": run_manager.get_child()})
            if isinstance(self.llm_chain, LLMChain):
                lines = response["text"]
            else:
                lines = response
            queries = lines[:max(options.options['chain']['num_queries']-1,0)]
            if self.include_original:
                queries.append(query)

            # Retrieve and combine documents for each query
            documents = []
            for query in queries:
                docs = self.retriever.invoke(query, config={"callbacks": run_manager.get_child()})
                documents.extend(docs)

            # Return unique union of retrieved documents
            return [doc for i, doc in enumerate(documents) if doc not in documents[:i]]

def create():
    """Set ChromaDB vectorstore (w/ options.options['chain']['collection_name']) as a retriever and create rag_chain"""
    prepare_models()
    prepare_prompts()
    
    vectorstore = Chroma(
        collection_name=options.options['chain']['collection_name'],
        embedding_function=embeddings,
        persist_directory=os.path.expanduser(embeddings_directory)
    )
    if options.options['chain']['rag_fusion']:
        retriever_multi = MultiQueryRetriever.from_llm(
            retriever=vectorstore.as_retriever(search_kwargs={'k': options.options['chain']['top_n_results_fusion']}),
            llm=model,
            include_original=True
        )
        retriever = create_history_aware_retriever(
            model, 
            retriever_multi, 
            contextualize_q_prompt
        )
    else:
        retriever = create_history_aware_retriever(
            model, 
            vectorstore.as_retriever(search_kwargs={'k': options.options['chain']['top_n_results']}), 
            contextualize_q_prompt
        )
    global rag_chain
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)