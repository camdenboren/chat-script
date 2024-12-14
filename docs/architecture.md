# Architecture

## Basic Flow

                                        __main__.py
                                             |
                ↓----------------------------↓---------------------------↓
    Create and/or Read options      Generate Embeddings            Launch App UI
          (options.py)                (embeddings.py)                (app.py)
                                                                         |
                                             ↓---------------------------↓
                                        Create chain      Pass response.generate to app UI
                               (chain.py, multi_retriever.py)      (response.py)

## Chain Details

    User Query + Chat History
            ↓
    Moderation Check
            ↓
    Generate Similar Queries
            ↓
    Retrieve Scripts for each Query
            ↓
    Pass User Query and Scripts to Chat Model

<i>Note: History, moderation, and rag-fusion are optional. If moderation is enabled and the query is deemed unsafe, stream a refusal response, skip following stages, and remove question from history on further iterations</i>

## Src Files

    __main__.py
    -Entry point of app
    -Sets up resources and directories if needed
    -Runs generate() from embeddings.py if needed
    -Runs launch() from app.py

    app.py
    -Launches Gradio UI leveraging generate() in response.py

    chain.py
    -Prepares language models
    -Creates moderation, rag chains

    embeddings.py
    -Generates script embeddings via embeddings model
    -Stores embeddings in persistent directory

    multi_retriever.py
    -Creates multi-query retriever

    options.py
    -Creates and reads options for entire app
    -Accessed via global dict

    response.py
    -Streams chat-model response with source-formatting
    -Uses chain constructed in chain.py
