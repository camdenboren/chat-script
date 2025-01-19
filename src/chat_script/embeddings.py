"""Refreshes/generates embeddings in based on scripts"""

# SPDX-FileCopyrightText: 2024-2025 Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import shutil

from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import TokenTextSplitter

from chat_script import options

# Directory and file names
SCRIPTS_DIR = "~/.chat-script/scripts"
EMBED_DIR = "~/.chat-script/embeddings"


def opt(option_name):
    """Syntactic sugar for retrieving options"""
    return options.OPTIONS["embeddings"][option_name]


def load():
    """Loads documents in SCRIPTS_DIR"""
    loader = DirectoryLoader(
        path=os.path.expanduser(SCRIPTS_DIR),
        loader_cls=TextLoader,
        show_progress=opt("show_progress"),
        use_multithreading=opt("use_multithreading"),
    )
    docs = loader.load()
    return docs


def create_batches(all_splits, batch_size):
    """Breaks all_splits into batches of size <= batch_size"""
    for i in range(0, len(all_splits), batch_size):
        yield all_splits[i : i + batch_size]


def split(docs):
    """Split documents, then divide into batches to avoid ChromaDB/SQLite batch size limitations"""
    text_splitter = TokenTextSplitter(
        chunk_size=opt("chunk_size"),
        chunk_overlap=opt("chunk_overlap"),
    )
    all_splits = text_splitter.split_documents(docs)
    all_splits = create_batches(all_splits, opt("batch_size"))
    return all_splits


def prepare_model():
    """Set and return Ollama embeddings model"""
    embeddings = OllamaEmbeddings(
        model=opt("embeddings_model"),
        base_url=opt("embeddings_url"),
        show_progress=opt("show_progress"),
    )
    return embeddings


def generate():
    """Embed and store text documents"""
    docs = load()
    all_splits = split(docs)
    embeddings = prepare_model()

    # Remove Vector Store if it exists
    if os.path.exists(os.path.expanduser(EMBED_DIR)):
        shutil.rmtree(os.path.expanduser(EMBED_DIR))

    # Save to persistent ChromaDB Vector Store
    for batch in all_splits:
        vectorstore = Chroma.from_documents(  # noqa: F841
            documents=batch,
            collection_name=opt("collection_name"),
            embedding=embeddings,
            persist_directory=os.path.expanduser(EMBED_DIR),
        )


if __name__ == "__main__":
    options.read()
    generate()
