# Refreshes/generates persistent embeddings in embeddings_directory based on text files in scripts_directory

import os
import shutil
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import TokenTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
import options

# Directory and file names
scripts_directory = "~/.chat-script/scripts"
embeddings_directory = "~/.chat-script/embeddings"

def generate():
    """Loads and chunks text documents, embeds them, then stores in persistent ChromaDB vectorstore"""
    # Load documents
    loader = DirectoryLoader(
        path=os.path.expanduser(scripts_directory), 
        loader_cls=TextLoader, 
        show_progress=options.options['embeddings']['show_progress'], 
        use_multithreading=options.options['embeddings']['use_multithreading']
    )
    docs = loader.load()

    # Split documents
    text_splitter = TokenTextSplitter(
        chunk_size=options.options['embeddings']['chunk_size'], 
        chunk_overlap=options.options['embeddings']['chunk_overlap']
    )
    all_splits = text_splitter.split_documents(docs)

    # Set embedding function 
    embeddings = OllamaEmbeddings(
        model=options.options['embeddings']['embeddings_model'], 
        show_progress=options.options['embeddings']['show_progress']
    )

    # Remove Vector Store if it exists
    if os.path.exists(os.path.expanduser(embeddings_directory)):
        shutil.rmtree(os.path.expanduser(embeddings_directory))

    # Save to persistent ChromaDB Vector Store
    vectorstore = Chroma.from_documents(
        documents=all_splits,
        collection_name=options.options['embeddings']['collection_name'],
        embedding=embeddings,
        persist_directory=os.path.expanduser(embeddings_directory)
    )

if __name__ == '__main__':
    generate()