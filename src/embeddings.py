# Refreshes/generates persistent embeddings in embeddings_directory based on text files in scripts_directory
# Run before using (can be executed as a script), and run after adding more files to scripts_directory

from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
import os
import shutil

#  Directory, collection names
scripts_directory = "~/.chat-script/scripts"
embeddings_directory = "~/.chat-script/embeddings"
collection_name = "rag-chroma"

# Model options
embeddings_model = "mxbai-embed-large"
show_progress = True

# Misc options 
use_multithreading = True
chunk_size = 500
chunk_overlap = 0

def check_scripts_dir():
    """Create scripts_directory if needed, otw run embeddings()"""
    if not os.path.exists(os.path.expanduser(scripts_directory)):
        os.makedirs(os.path.expanduser(scripts_directory))
        print("\nCreated scripts_directory at: " + scripts_directory)
        user_embed = None
        while not user_embed:
            user_embed = str(input("Would you like to embed the scripts now (add your scripts to ~/.chat-script/scripts before submitting)? y/n: "))
            if user_embed:
                if user_embed[0] == "y" or user_embed[0] == "Y":
                    embeddings()
                elif user_embed[0] == "n" or user_embed[0] == "N":
                    break
                else:
                    print("Input must be one of: y/n\n")
                user_embed = None
    else:
        embeddings()

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
        perist_directory=os.path.expanduser(embeddings_directory)
    )

if __name__ == '__main__':
    check_scripts_dir()