#!/usr/bin/env python

# Refreshes/generates persistent embeddings in persist_directory based on text files in document_directory
# Run before using (can be executed as a script), and run after adding more files to document_directory

from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
import os
import shutil

# Model options and directory, collection names
document_directory = "~/.chat-script/scripts"
persist_directory = "~/.chat-script/embeddings"
embeddings_model = "all-MiniLM-L6-v2"
collection_name = "rag-chroma"

# Create document_directory if needed 
def check_doc_dir():
    if not os.path.exists(os.path.expanduser(document_directory)):
        os.makedirs(os.path.expanduser(document_directory))
        print("\nCreated document_directory at: " + document_directory + ". Add your documents there and run 'nix develop github:camdenboren/chat-script --command bash -c \"python src/embeddings.py\" to embed them.")
    else:
        embeddings()

# Loads and chunks text documents, embeds them, then stores in persistent ChromaDB vectorstore
def embeddings():
    # Load documents
    loader = DirectoryLoader(path=os.path.expanduser(document_directory), loader_cls=TextLoader, show_progress=True, use_multithreading=True)
    docs = loader.load()

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    all_splits = text_splitter.split_documents(docs)

    # Set embedding function 
    embeddings = SentenceTransformerEmbeddings(model_name=embeddings_model)

    # Remove Vector Store if it exists
    if os.path.exists(os.path.expanduser(persist_directory)):
        shutil.rmtree(os.path.expanduser(persist_directory))

    # Save to persistent ChromaDB Vector Store
    vectorstore = Chroma.from_documents(
        documents=all_splits,
        collection_name=collection_name,
        embedding=embeddings,
        persist_directory=os.path.expanduser(persist_directory)
    )

if __name__ == '__main__':
    check_doc_dir()