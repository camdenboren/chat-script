# Options


To adjust these options, edit:

    ~/.config/chat-script/chat-script.ini

## App

| Option        | Desc                                                                               | Default       |
| ------------- | ---------------------------------------------------------------------------------- | ------------- |
| share         | Whether to create a publicly shareable link for the gradio app                     | False         |
| server_name   | IP address that local app is deployed at                                           | 127.0.0.1     |
| server_port   | Port that local app is deployed at                                                 | 7860          |
| inbrowser     | Whether to automatically launch the gradio app in a new tab on the default browser | True          |

## Chain

| Option               | Desc          | Default                |
| -------------------- | ------------- | ---------------------- |
| embeddings_model     | Name of Ollama LLM used to generate embeddings                                                                                     | mxbai-embed-large      |
| chat_model           | Name of Ollama LLM used to generate responses                                                                                      | mistral                |
| moderation_model     | Name of Ollama LLM used to moderate queries                                                                                        | xe/llamaguard3         |
| chat_url             | URL of Ollama LLM used to generate responses                                                                                       | http://localhost:11434 |
| moderation_url       | URL of Ollama LLM used to moderate queries                                                                                         | http://localhost:11434 |
| show_progress        | Whether to display embeddings model batch progress                                                                                 | False                  |
| keep_alive           | How long the model will stay loaded into memory                                                                                    | 5m                     |
| temperature          | The temperature of the chat model. Increasing the temperature will make the model answer more creatively                           | 0.6                    |
| top-k | Reduces the probability of generating nonsense. A higher value will give more diverse answers, while a lower value will be more conservative      | 30                     |
| top-p                | Works together with top-k. A higher value will lead to more diverse text, while a lower value will generate more conservative text | 0.7                    |
| collection_name      | Name of local document collection                                                                                                  | rag-chroma             |
| top_n_results        | Amount of documents to return                                                                                                      | 3                      |
| rag_fusion           | Whether to enable rag-fusion, an advanced rag technique that may improve semantic search relevance                                 | True                   |
| num_queries          | Number of synthetic queries to generate for rag-fusion                                                                             | 2                      |
| top_n_results_fusion | Maximum amount of documents to return for rag-fusion (maximum, as unique union is taken)                                           | 2                      |
| embeddings_gpu       | Whether to use the GPU when generating embeddings (on devices with <8GB VRAM, setting to False can reduce latency)                 | True                   |

## Embeddings

| Option             | Desc                                                                    | Default           |
| ------------------ | ----------------------------------------------------------------------- | ----------------- |
| embeddings_model   | Name of Ollama LLM used to generate embeddings                          | mxbai-embed-large |
| show_progress      | Whether to display document loading and embeddings model batch progress | True              |
| collection_name    | Name of local document collection                                       | rag-chroma        |
| use_multithreading | Whether to enable CPU multithreading for loading documents              | True              |
| chunk_size         | Number of tokens in each split document chunk                           | 250               |
| chunk_overlap      | Number of tokens shared between consecutive split document chunks       | 50                |
| batch_size         | Maximum number of split documents in each embeddings batch              | 41666             |

## Response

| Option               | Desc                                                                                                                                                                      | Default       |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| context_stream_delay | Amount of time in s to delay tokens streamed for non-LLM text (sources, moderation notice)                                                                                | 0.075         |
| max_history          | Maximum number of previous user messages to include as context                                                                                                            | 2             |
| print_state          | Whether to print app state for each query. Includes: IP address, chat history, and context                                                                                | True          |
| moderate             | Whether to moderate user queries before allowing responses. Prints IP address and offending query even if print_state is false (allows for privacy-preserving moderation) | False         |
| moderate_alert       | Whether to display system alerts when an unsafe question is received                                                                                                      | False         |
