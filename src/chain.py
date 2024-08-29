# Setup language models and multi-query retriever, define the moderation and rag chains

import os
from langchain_community.embeddings import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_chroma import Chroma
import options
import multi_retriever

# Directory and file names
embeddings_directory = "~/.chat-script/embeddings"

def opt(option_name):
    """Syntactic sugar for retrieving options"""
    return options.options['chain'][option_name]

def prepare_models():
    # Set num_gpu depending on whether opt('embeddings_gpu') is True or False
    if opt('embeddings_gpu'):
        num_gpu = None
    else:
        num_gpu = 0

    # Set Embedding LLM to local Ollama model
    embeddings = OllamaEmbeddings(
        model=opt('embeddings_model'), 
        show_progress=opt('show_progress'), 
        num_gpu=num_gpu
    )

    # Set LLM to local Ollama model
    model = ChatOllama(
        model=opt('chat_model'),
        keep_alive=opt('keep_alive'),
        base_url=opt('chat_url'),
        temperature=opt('temperature'),
        top_k=opt('top_k'),
        top_p=opt('top_p')
    )

    return embeddings, model

def prepare_prompts():
    # Define the contextualization prompt for summarizing chat history
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),    
    ])

    # Define the question_answer_chain 
    system_prompt = (
        "Answer the question using the following context: "
        "{context}"
    )
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    return qa_prompt, contextualize_q_prompt

def create():
    """Set ChromaDB vectorstore (w/ opt('collection_name')) as a retriever and create rag_chain"""
    embeddings, model = prepare_models()
    qa_prompt, contextualize_q_prompt = prepare_prompts()
    question_answer_chain = create_stuff_documents_chain(model, qa_prompt)

    vectorstore = Chroma(
        collection_name=opt('collection_name'),
        embedding_function=embeddings,
        persist_directory=os.path.expanduser(embeddings_directory)
    )
    if opt('rag_fusion'):
        MultiQueryRetriever = multi_retriever.prepare(opt('num_queries'))
        retriever_fusion = MultiQueryRetriever.from_llm(
            retriever=vectorstore.as_retriever(search_kwargs={'k': opt('top_n_results_fusion')}),
            llm=model,
            include_original=True
        )
        retriever = create_history_aware_retriever(
            model, 
            retriever_fusion, 
            contextualize_q_prompt
        )
    else:
        retriever = create_history_aware_retriever(
            model, 
            vectorstore.as_retriever(search_kwargs={'k': opt('top_n_results')}), 
            contextualize_q_prompt
        )
    global rag_chain
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

def create_moderation():
    """Set Moderation LLM to local Ollama model, construct and return chain"""
    moderation = ChatOllama(
        model=opt('moderation_model'),
        keep_alive=opt('keep_alive'),
        base_url=opt('moderation_url')
    )
    moderation_chain = moderation | StrOutputParser()
    return moderation_chain