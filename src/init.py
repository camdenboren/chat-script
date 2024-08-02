#!/usr/bin/env python

# Entry point that ensures necessary config and scripts are setup before handing off to app.py

import app as a
import embeddings as e
import os
from configparser import ConfigParser

configuration = ConfigParser()

# Directory names
scripts_directory = "~/.chat-script/scripts"
embeddings_directory = "~/.chat-script/embeddings"
config_directory = "~/.config/chat-script"
config_file = config_directory + "/chat-script.ini"

def init():
    """Create directories and embed scripts if needed, otw run app()"""
    if not os.path.exists(os.path.expanduser(config_directory)):
        os.makedirs(os.path.expanduser(config_directory))
        configuration['APP'] = {'share': 'False'}
        configuration['RESPONSE'] = {'collection_name': 'rag-chroma',
                              'embeddings_model': 'mxbai-embed-large',
                              'chat_model': 'mistral',
                              'moderation_model': 'xe/llamaguard3',
                              'show_progress': 'False',
                              'keep_alive': '5m',
                              'temperature': '0.6',
                              'top_k': '30',
                              'top_p': '0.7',
                              'moderate': 'False',
                              'top_n_results': '3',
                              'context_stream_delay': '0.075',
                              'print_state': 'True'}
        configuration['EMBEDDINGS'] = {'collection_name': 'rag-chroma',
                              'embeddings_model': 'mxbai-embed-large',
                              'show_progress': 'True',
                              'use_multithreading': 'True',
                              'chunk_size': '500',
                              'chunk_overlap': '0'}          
        with open(os.path.expanduser(config_file), 'w') as configfile:
            configuration.write(configfile)
        print("\nCreated config_directory at: " + config_directory + " and populated it with default settings")
        if os.path.exists(os.path.expanduser(scripts_directory)):
            a.app()
    elif not os.path.exists(os.path.expanduser(scripts_directory)):
        os.makedirs(os.path.expanduser(scripts_directory))
        print("\nCreated scripts_directory at: " + scripts_directory)
        user_embed = None
        while not user_embed:
            user_embed = str(input("Would you like to embed the scripts now (if yes, then add your scripts to ~/.chat-script/scripts before submitting)? y/n: "))
            if user_embed:
                if user_embed[0] == "y" or user_embed[0] == "Y":
                    e.embeddings()
                    a.app()
                elif user_embed[0] == "n" or user_embed[0] == "N":
                    a.app()
                else:
                    print("Input must be one of: y/n\n")
                    user_embed = None
    else:
        a.app()

if __name__ == '__main__':
    init()