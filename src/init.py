#!/usr/bin/env python

# Entry point that ensures necessary config and scripts are setup before handing off to app.py

import os
from configparser import ConfigParser
from app import app
from embeddings import embeddings

# Directory and file names
scripts_directory = "~/.chat-script/scripts"
embeddings_directory = "~/.chat-script/embeddings"
config_directory = "~/.config/chat-script"
config_file = config_directory + "/chat-script.ini"

def init():
    """Create directories and embed scripts if needed, otw run app()"""
    if not os.path.exists(os.path.expanduser(config_file)):
        if not os.path.exists(os.path.expanduser(config_directory)):
            os.makedirs(os.path.expanduser(config_directory))
        configuration = ConfigParser()
        configuration['APP'] = {
            'share': 'False',
            'server_name': '127.0.0.1',
            'server_port': '7860',
            'inbrowser': 'True'
        }
        configuration['RESPONSE'] = {
            'context_stream_delay': '0.075',
            'max_history': '2',
            'print_state': 'True'
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
            'top_p': '0.7','collection_name': 'rag-chroma',
            'top_n_results': '3',
            'moderate': 'False',
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
            'chunk_size': '300',
            'chunk_overlap': '100'
        }
        with open(os.path.expanduser(config_file), 'w') as configfile:
            configuration.write(configfile)
        print("\nCreated config_file at: " + config_file + " and populated it with default settings")
        if os.path.exists(os.path.expanduser(scripts_directory)):
            app()
    elif not os.path.exists(os.path.expanduser(scripts_directory)):
        os.makedirs(os.path.expanduser(scripts_directory))
        print("\nCreated scripts_directory at: " + scripts_directory)
        user_embed = None
        while not user_embed:
            user_embed = str(input("Would you like to embed the scripts now (if yes, then add your scripts to ~/.chat-script/scripts before submitting)? y/n: "))
            if user_embed:
                if user_embed[0] == "y" or user_embed[0] == "Y":
                    embeddings()
                    app()
                elif user_embed[0] == "n" or user_embed[0] == "N":
                    app()
                else:
                    print("Input must be one of: y/n\n")
                    user_embed = None
    else:
        app()

if __name__ == '__main__':
    init()