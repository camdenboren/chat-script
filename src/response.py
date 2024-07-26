# Returns response w/ citations from RAG-enabled LLM based on user question passed from app ui

from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
import time as t
import os

# Model options and directory, collection names
scripts_directory = "~/.chat-script/scripts"
embeddings_directory = "~/.chat-script/embeddings"
embeddings_model = "mxbai-embed-large"
chat_model = "mistral"
collection_name = "rag-chroma"
context_stream_delay = 0.075

# Calculate length of scripts_dir name for citation formatting later
scripts_dir_len = len(os.path.expanduser(scripts_directory))
if scripts_directory[-1] != "/":
    scripts_dir_len += 1

# Set Embedding Function
embeddings = OllamaEmbeddings(model=embeddings_model, show_progress=True)

# Set ChromaDB vectorstore as retriever
vectorstore = Chroma(
    collection_name=collection_name,
    embedding_function=embeddings,
    persist_directory=os.path.expanduser(embeddings_directory)
)
retriever = vectorstore.as_retriever(search_kwargs={'k': 3})

# Define the prompt via a template leveraging provided context
template = """Answer the question using the following context. If you use any information in the context, include the index (like: [1]) of the relevant Document as an in-text citation in your answer, and nothing else. Remember that each Document has two sections: page_content, and metadata- don't confuse these for indexable objects.
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

# Set LLM to local Ollama model
model = ChatOllama(model=chat_model)

# Print state (includes question, context) - useful for debugging and finding exact quotes
def inspect(state):
    """Print the state passed between Runnables in a langchain and pass it on"""
    print("\n")
    print(state)
    return state
    
# Formats and yields context passed to LLM in human-readable format
def format_context(context):
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

# Creates langchain w/ local LLM, then streams chain's text response
def response(question,history):
    # Define the langchain
    rag_chain_from_docs = (
        RunnableLambda(inspect)
        | prompt
        | model
        | StrOutputParser()
    )
    retrieve_docs = (lambda x: x["question"]) | retriever
    chain = RunnablePassthrough.assign(context=retrieve_docs).assign(answer=rag_chain_from_docs)

    # Return/yield response and formatted context (if applicable) as a text stream
    result = chain.stream({"question": question})
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