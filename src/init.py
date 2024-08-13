#!/usr/bin/env python

# Entry point that ensures necessary config and scripts are setup before handing off to app.py

import os
from options import create_options, read_options

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
            create_options()
        if os.path.exists(os.path.expanduser(scripts_directory)):
            read_options()
            from app import app
            app()
    elif not os.path.exists(os.path.expanduser(scripts_directory)):
        os.makedirs(os.path.expanduser(scripts_directory))
        print("\nCreated scripts_directory at: " + scripts_directory)
        user_embed = None
        while not user_embed:
            user_embed = str(input("Would you like to embed the scripts now (if yes, then add your scripts to ~/.chat-script/scripts before submitting)? y/n: "))
            if user_embed:
                if user_embed[0] == "y" or user_embed[0] == "Y":
                    read_options()
                    from embeddings import embeddings
                    embeddings()
                    from app import app
                    app()
                elif user_embed[0] == "n" or user_embed[0] == "N":
                    read_options()
                    from app import app
                    app()
                else:
                    print("Input must be one of: y/n\n")
                    user_embed = None
    else:
        read_options()
        from app import app
        app()

if __name__ == '__main__':
    init()