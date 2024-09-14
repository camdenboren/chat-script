"""Refreshes/generates embeddings in based on scripts"""

import os
import shutil
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import TokenTextSplitter
from langchain_chroma import Chroma
import options

# Directory and file names
SCRIPTS_DIR = "~/.chat-script/scripts"
EMBED_DIR = "~/.chat-script/embeddings"

def opt(option_name):
    """Syntactic sugar for retrieving options"""
    return options.OPTIONS['embeddings'][option_name]

def create_batches(all_splits, batch_size):
    """Breaks all_splits into batches of size <= batch_size"""
    for i in range(0, len(all_splits), batch_size):
        yield all_splits[i:i + batch_size]

def generate():
    """Loads, chunks, embeds, stores text documents"""
    # Load documents
    loader = DirectoryLoader(
        path=os.path.expanduser(SCRIPTS_DIR),
        loader_cls=TextLoader,
        show_progress=opt('show_progress'),
        use_multithreading=opt('use_multithreading')
    )
    docs = loader.load()

    # Split documents, then divide into batches to avoid ChromaDB/SQLite batch size limitations
    text_splitter = TokenTextSplitter(
        chunk_size=opt('chunk_size'),
        chunk_overlap=opt('chunk_overlap')
    )
    all_splits = text_splitter.split_documents(docs)
    all_splits = create_batches(all_splits, opt('batch_size'))

    # Set embedding function
    embeddings = OllamaEmbeddings(
        model=opt('embeddings_model'),
        show_progress=opt('show_progress')
    )

    # Remove Vector Store if it exists
    if os.path.exists(os.path.expanduser(EMBED_DIR)):
        shutil.rmtree(os.path.expanduser(EMBED_DIR))

    # Save to persistent ChromaDB Vector Store
    for batch in all_splits:
        vectorstore = Chroma.from_documents(
            documents=batch,
            collection_name=opt('collection_name'),
            embedding=embeddings,
            persist_directory=os.path.expanduser(EMBED_DIR)
        )

if __name__ == '__main__':
    options.read()
    generate()
