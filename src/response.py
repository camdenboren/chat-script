# Returns response w/ citations from RAG-enabled LLM based on user question passed from app ui

import os
import time as t
from configparser import ConfigParser
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from gradio import Request

# Directory and file names
scripts_directory = "~/.chat-script/scripts"
embeddings_directory = "~/.chat-script/embeddings"
config_file = "~/.config/chat-script/chat-script.ini"

# Set options
configuration = ConfigParser()
configuration.read(os.path.expanduser(config_file))
embeddings_model = configuration.get("RESPONSE", "embeddings_model", fallback="mxbai-embed-large")
chat_model = configuration.get("RESPONSE", "chat_model", fallback="mistral")
moderation_model = configuration.get("RESPONSE", "moderation_model", fallback="xe/llamaguard3")
show_progress = configuration.getboolean("RESPONSE", "show_progress", fallback=False)
keep_alive = configuration.get("RESPONSE", "keep_alive", fallback="5m")
temperature = configuration.getfloat("RESPONSE", "temperature", fallback=0.6)
top_k =  configuration.getint("RESPONSE", "top_k", fallback=30)
top_p = configuration.getfloat("RESPONSE", "top_p", fallback=0.7)
collection_name = configuration.get("RESPONSE", "collection_name", fallback="rag-chroma")
moderate = configuration.getboolean("RESPONSE", "moderate", fallback=False)
top_n_results = configuration.getint("RESPONSE", "top_n_results", fallback=3)
context_stream_delay = configuration.getfloat("RESPONSE", "context_stream_delay", fallback=0.075)
max_history = configuration.getint("RESPONSE", "max_history", fallback=2)
print_state = configuration.getboolean("RESPONSE", "print_state", fallback=True)

# Calculate length of scripts_dir name for citation formatting later
scripts_dir_len = len(os.path.expanduser(scripts_directory))
if scripts_directory[-1] != "/":
    scripts_dir_len += 1

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
        keep_alive=keep_alive
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
    global retriever
    retriever = create_history_aware_retriever(model, vectorstore.as_retriever(search_kwargs={'k': top_n_results}), contextualize_q_prompt)
    
def format_context(context):
    """Formats and yields context passed to LLM in human-readable format"""
    if print_state:
        print("Context: ", context, sep="")
    formatted_context = "Relevant Sources (some may not have been used): "
    index = 0
    yield "\n\n"
    while(index < len(context)):
        formatted_context += "[" + str(index+1) + "] " + context[index].metadata["source"][scripts_dir_len:]
        for chunks in formatted_context.split():
            yield chunks + " "
            if((index == 0) and (chunks == "used):")):
                yield "\n"
            t.sleep(context_stream_delay)
        yield "\n"
        formatted_context = ""
        index += 1

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Manage chat history"""
    return session_history

def inspect(state):
    """Print state between runnables and pass it on (includes: input, chat_history)"""
    if print_state:
        print("State: ", state, sep="")
    return state

def response(question,history,request: Request):
    """Checks question for safety (if applicable) then creates RAG + history chain w/ local LLM and streams chain's text response"""
    if request and print_state:
        print("\nIP address of user: ", request.client.host, sep="")
    allow_response = True
    if moderate:
        check_question = moderation_chain.invoke(question)
        allow_response = (check_question[2:6] == "safe")
    if allow_response:
        # Workaround for converting Gradio history to Langchain-compatible chat_history
        # Separates chat_history by user and lets Clear on Gradio UI do its job
        global session_history
        session_history = ChatMessageHistory()
        if len(history) > max_history:
            history = history[-max_history:]
        for msgs in history:
            session_history.add_user_message(msgs[0])
            session_history.add_ai_message(msgs[1].split("\n\nRelevant Sources")[0])
        
        # Define retrieval chain w/ history
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        chain = RunnableWithMessageHistory(
            RunnableLambda(inspect) | rag_chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
        # Old approach for including context in state - investigate this further to prevent separate context printing
        #retrieve_docs = (lambda x: x["input"]) | retriever
        #chain = RunnablePassthrough.assign(context=retrieve_docs).assign(answer=rag_chain_from_docs)

        # Return/yield response and formatted context (if applicable) as a text stream
        result = chain.stream({"input": question},config={"configurable": {"session_id": "unused"}})
        response_stream = ""
        context = None
        for chunks in result:
            answer_chunks = chunks.get("answer")
            get_context = chunks.get("context")
            if(answer_chunks):
                response_stream += answer_chunks
            if(get_context):
                context = get_context
            yield response_stream
        if context:
            formatted_context = format_context(context)
            for context_chunks in formatted_context:
                response_stream += context_chunks
                yield response_stream
    else:
        yield "Your question is unsafe, so no response will be provided."
        print("Unsafe question: \'", question, "\'", sep="")