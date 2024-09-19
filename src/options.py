"""Creates and reads options at ~/.config/chat-script/chat-script.ini"""

import os
from configparser import ConfigParser

CONFIG_DIR = "~/.config/chat-script"
CONFIG_FILE = f"{CONFIG_DIR}/chat-script.ini"

def create():
    """Create options file at ~/.config/chat-script/chat-script.ini with defaults"""
    configuration = ConfigParser()
    configuration['APP'] = {
        'share': 'False',
        'server_name': '127.0.0.1',
        'server_port': '7860',
        'inbrowser': 'True'
    }
    configuration['CHAIN'] = {
        'embeddings_model': 'mxbai-embed-large',
        'chat_model': 'mistral',
        'moderation_model': 'xe/llamaguard3',
        'chat_url': 'http://localhost:11434',
        'moderation_url': 'http://localhost:11434',
        'show_progress': 'False',
        'keep_alive': '5m',
        'temperature': '0.6',
        'top_k': '30',
        'top_p': '0.7',
        'collection_name': 'rag-chroma',
        'top_n_results': '3',
        'rag_fusion': 'True',
        'num_queries': '2',
        'top_n_results_fusion': '2',
        'embeddings_gpu': 'True'
    }
    configuration['EMBEDDINGS'] = {
        'embeddings_model': 'mxbai-embed-large',
        'show_progress': 'True',
        'collection_name': 'rag-chroma',
        'use_multithreading': 'True',
        'chunk_size': '250',
        'chunk_overlap': '50',
        'batch_size': '41666'
    }
    configuration['RESPONSE'] = {
        'context_stream_delay': '0.075',
        'max_history': '2',
        'print_state': 'True',
        'moderate': 'False',
        'moderate_alert': 'False'
    }
    with open(os.path.expanduser(CONFIG_FILE), 'w', encoding='UTF-8') as configfile:
        configuration.write(configfile)
    print(f"\nCreated CONFIG_FILE at: {CONFIG_FILE} and populated it with default settings")

def read():
    """Read options from ~/.config/chat-script/chat-script.ini and save in global dict: options"""
    configuration = ConfigParser()
    configuration.read(os.path.expanduser(CONFIG_FILE))
    global OPTIONS
    OPTIONS = {
        'app': {
            'share': configuration.getboolean(
                "APP",
                "share",
                fallback=False
            ),
            'server_name': configuration.get(
                "APP",
                "server_name",
                fallback="127.0.0.1"
            ),
            'server_port': configuration.getint(
                "APP",
                "server_port",
                fallback=7860
            ),
            'inbrowser': configuration.getboolean(
                "APP",
                "inbrowser",
                fallback=True
            )
        },
        'chain': {
            'embeddings_model': configuration.get(
                "CHAIN",
                "embeddings_model",
                fallback="mxbai-embed-large"
            ),
            'chat_model': configuration.get(
                "CHAIN",
                "chat_model",
                fallback="mistral"
            ),
            'moderation_model': configuration.get(
                "CHAIN",
                "moderation_model",
                fallback="xe/llamaguard3"
            ),
            'chat_url': configuration.get(
                "CHAIN",
                "chat_url",
                fallback="http://localhost:11434"
            ),
            'moderation_url': configuration.get(
                "CHAIN",
                "moderation_url",
                fallback="http://localhost:11434"
            ),
            'show_progress': configuration.getboolean(
                "CHAIN",
                "show_progress",
                fallback=False
            ),
            'keep_alive': configuration.get(
                "CHAIN",
                "keep_alive",
                fallback="5m"
            ),
            'temperature': configuration.getfloat(
                "CHAIN",
                "temperature",
                fallback=0.6
            ),
            'top_k':  configuration.getint(
                "CHAIN",
                "top_k",
                fallback=30
            ),
            'top_p': configuration.getfloat(
                "CHAIN",
                "top_p",
                fallback=0.7
            ),
            'collection_name': configuration.get(
                "CHAIN",
                "collection_name",
                fallback="rag-chroma"
            ),
            'top_n_results': configuration.getint(
                "CHAIN",
                "top_n_results",
                fallback=3
            ),
            'rag_fusion': configuration.getboolean(
                "CHAIN",
                "rag_fusion",
                fallback=True
            ),
            'num_queries': configuration.getint(
                "CHAIN",
                "num_queries",
                fallback=2
            ),
            'top_n_results_fusion': configuration.getint(
                "CHAIN",
                "top_n_results_fusion",
                fallback=2
            ),
            'embeddings_gpu': configuration.getboolean(
                "CHAIN",
                "embeddings_gpu",
                fallback=True
            )
        },
        'embeddings': {
            'embeddings_model': configuration.get(
                "EMBEDDINGS",
                "embeddings_model",
                fallback="mxbai-embed-large"
            ),
            'show_progress': configuration.getboolean(
                "EMBEDDINGS",
                "show_progress",
                fallback=True
            ),
            'collection_name': configuration.get(
                "EMBEDDINGS",
                "collection_name",
                fallback="rag-chroma"
            ),
            'use_multithreading': configuration.getboolean(
                "EMBEDDINGS",
                "use_multithreading",
                fallback=True
            ),
            'chunk_size': configuration.getint(
                "EMBEDDINGS",
                "chunk_size",
                fallback=250
            ),
            'chunk_overlap': configuration.getint(
                "EMBEDDINGS",
                "chunk_overlap",
                fallback=50
            ),
            'batch_size': configuration.getint(
                "EMBEDDINGS",
                "batch_size",
                fallback=41666
            )
        },
        'response': {
            'context_stream_delay': configuration.getfloat(
                "RESPONSE",
                "context_stream_delay",
                fallback=0.075
            ),
            'max_history': configuration.getint(
                "RESPONSE",
                "max_history",
                fallback=2
            ),
            'print_state': configuration.getboolean(
                "RESPONSE",
                "print_state",
                fallback=True
            ),
            'moderate': configuration.getboolean(
                "RESPONSE",
                "moderate",
                fallback=False
            ),
            'moderate_alert': configuration.getboolean(
                "RESPONSE",
                "moderate_alert",
                fallback=False
            )
        }
    }
