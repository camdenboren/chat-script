# Setup language models and retriever, define the moderation and rag chains

import os
from configparser import ConfigParser
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_community.vectorstores import Chroma

# Directory and file names
embeddings_directory = "~/.chat-script/embeddings"
config_file = "~/.config/chat-script/chat-script.ini"

# Set options
configuration = ConfigParser()
configuration.read(os.path.expanduser(config_file))
embeddings_model = configuration.get("CHAIN", "embeddings_model", fallback="mxbai-embed-large")
chat_model = configuration.get("CHAIN", "chat_model", fallback="mistral")
moderation_model = configuration.get("CHAIN", "moderation_model", fallback="xe/llamaguard3")
chat_url = configuration.get("CHAIN", "chat_url", fallback="http://localhost:11434")
moderation_url = configuration.get("CHAIN", "moderation_url", fallback="http://localhost:11434")
show_progress = configuration.getboolean("CHAIN", "show_progress", fallback=False)
keep_alive = configuration.get("CHAIN", "keep_alive", fallback="5m")
temperature = configuration.getfloat("CHAIN", "temperature", fallback=0.6)
top_k =  configuration.getint("CHAIN", "top_k", fallback=30)
top_p = configuration.getfloat("CHAIN", "top_p", fallback=0.7)
collection_name = configuration.get("CHAIN", "collection_name", fallback="rag-chroma")
top_n_results = configuration.getint("CHAIN", "top_n_results", fallback=3)
moderate = configuration.getboolean("CHAIN", "moderate", fallback=False)

# Set Embedding LLM to local Ollama model
embeddings = OllamaEmbeddings(model=embeddings_model, show_progress=show_progress)

# Set LLM to local Ollama model
model = ChatOllama(
    model=chat_model,
    show_progress=show_progress,
    keep_alive=keep_alive,
    temperature=temperature,
    top_k=top_k,
    top_p=top_p
)

# Set Moderation LLM to local Ollama model
if moderate:
    moderation = ChatOllama(
        model=moderation_model,
        show_progress=show_progress,
        keep_alive=keep_alive,
        base_url=moderation_url
    )
    moderation_chain = moderation | StrOutputParser()

# Define the question_answer_chain 
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
system_prompt = (
    "Answer the question using the following context. If you use any information in the context, include the index (like: [1]) of the relevant Document as an in-text citation in your answer, and nothing else. Remember that each Document has two sections: page_content, and metadata- don't confuse these for indexable objects."
    "{context}"
)
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
question_answer_chain = create_stuff_documents_chain(model, qa_prompt)

def set_vectorstore():
    """Set ChromaDB vectorstore (w/ collection_name) as a retriever"""
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=os.path.expanduser(embeddings_directory)
    )
    retriever = create_history_aware_retriever(
        model, 
        vectorstore.as_retriever(search_kwargs={'k': top_n_results}), 
        contextualize_q_prompt
    )
    global rag_chain
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)