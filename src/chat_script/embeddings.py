# SPDX-FileCopyrightText: Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

"""Refreshes/generates embeddings in based on scripts"""

import os
import shutil
from typing import Iterator

from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.documents.base import Document
from langchain_text_splitters import TokenTextSplitter

from chat_script import options

# Directory and file names
SCRIPTS_DIR = "~/.chat-script/scripts"
EMBED_DIR = "~/.chat-script/embeddings"


def opt(option_name: str) -> bool | str | int | float:
    """Syntactic sugar for retrieving options"""
    return options.OPTIONS["embeddings"][option_name]


def load() -> list[Document]:
    """Loads documents in SCRIPTS_DIR"""
    loader = DirectoryLoader(
        path=os.path.expanduser(SCRIPTS_DIR),
        loader_cls=TextLoader,
        show_progress=bool(opt("show_progress")),
        use_multithreading=bool(opt("use_multithreading")),
    )
    docs = loader.load()
    return docs


def create_batches(
    all_splits: list[Document], batch_size: int
) -> Iterator[list[Document]]:
    """Breaks all_splits into batches of size <= batch_size"""
    for i in range(0, len(all_splits), batch_size):
        yield all_splits[i : i + batch_size]


def split(docs: list[Document]) -> Iterator[list[Document]]:
    """Split documents, then divide into batches to avoid ChromaDB/SQLite batch size limitations"""
    text_splitter = TokenTextSplitter(
        chunk_size=opt("chunk_size"),
        chunk_overlap=opt("chunk_overlap"),
    )
    all_splits = text_splitter.split_documents(docs)
    all_splits = create_batches(all_splits, int(opt("batch_size")))
    return all_splits


def prepare_model() -> OllamaEmbeddings:
    """Set and return Ollama embeddings model"""
    embeddings = OllamaEmbeddings(
        model=str(opt("embeddings_model")),
        base_url=str(opt("embeddings_url")),
        show_progress=bool(opt("show_progress")),
    )
    return embeddings


def generate() -> None:
    """Embed and store text documents"""
    docs = load()
    all_splits = split(docs)
    embeddings = prepare_model()

    # Remove Vector Store if it exists
    if os.path.exists(os.path.expanduser(EMBED_DIR)):
        shutil.rmtree(os.path.expanduser(EMBED_DIR))

    # Save to persistent ChromaDB Vector Store
    for batch in all_splits:
        _vectorstore = Chroma.from_documents(  # pyright: ignore [reportUnknownMemberType]
            documents=batch,
            collection_name=str(opt("collection_name")),
            embedding=embeddings,
            persist_directory=os.path.expanduser(EMBED_DIR),
        )


if __name__ == "__main__":
    options.read()
    generate()
