# Refreshes/generates persistent embeddings in embeddings_directory based on text files in scripts_directory

from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
import os
import shutil
from configparser import ConfigParser

#  Directory names
scripts_directory = "~/.chat-script/scripts"
embeddings_directory = "~/.chat-script/embeddings"
config_file = "~/.config/chat-script/chat-script.ini"

# Set options
if not os.path.exists(os.path.expanduser(config_file)):
    # Model options
    embeddings_model = "mxbai-embed-large"
    show_progress = True

    # Misc options 
    collection_name = "rag-chroma"
    use_multithreading = True
    chunk_size = 500
    chunk_overlap = 0
else:
    configuration = ConfigParser()
    configuration.read(os.path.expanduser(config_file))

    # Model Options
    embeddings_model = configuration.get("EMBEDDINGS","embeddings_model")
    show_progress = configuration.getboolean("EMBEDDINGS","show_progress")

    # Misc options 
    collection_name = configuration.get("EMBEDDINGS","collection_name")
    use_multithreading = configuration.getboolean("EMBEDDINGS","use_multithreading")
    chunk_size = configuration.getint("EMBEDDINGS","chunk_size")
    chunk_overlap = configuration.getint("EMBEDDINGS","chunk_overlap")

def embeddings():
    """Loads and chunks text documents, embeds them, then stores in persistent ChromaDB vectorstore"""
    # Load documents
    loader = DirectoryLoader(
        path=os.path.expanduser(scripts_directory), 
        loader_cls=TextLoader, 
        show_progress=show_progress, 
        use_multithreading=use_multithreading
    )
    docs = loader.load()

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    all_splits = text_splitter.split_documents(docs)

    # Set embedding function 
    embeddings = OllamaEmbeddings(model=embeddings_model, show_progress=show_progress)

    # Remove Vector Store if it exists
    if os.path.exists(os.path.expanduser(embeddings_directory)):
        shutil.rmtree(os.path.expanduser(embeddings_directory))

    # Save to persistent ChromaDB Vector Store
    vectorstore = Chroma.from_documents(
        documents=all_splits,
        collection_name=collection_name,
        embedding=embeddings,
        persist_directory=os.path.expanduser(embeddings_directory)
    )

if __name__ == '__main__':
    embeddings()