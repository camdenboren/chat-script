#!/usr/bin/env python

# Entry point that ensures necessary config and scripts are setup before handing off to app.py

import os
import app
import embeddings
import options

# Directory and file names
scripts_directory = "~/.chat-script/scripts"
embeddings_directory = "~/.chat-script/embeddings"
config_directory = "~/.config/chat-script"
config_file = config_directory + "/chat-script.ini"

def init():
    """Create directories and embed scripts if needed, otw run launch()"""
    if not os.path.exists(os.path.expanduser(config_file)):
        if not os.path.exists(os.path.expanduser(config_directory)):
            os.makedirs(os.path.expanduser(config_directory))
            options.create()
        if os.path.exists(os.path.expanduser(scripts_directory)):
            options.read()
            app.launch()
    elif not os.path.exists(os.path.expanduser(scripts_directory)):
        os.makedirs(os.path.expanduser(scripts_directory))
        print("\nCreated scripts_directory at: " + scripts_directory)
        user_embed = None
        while not user_embed:
            user_embed = str(input("Would you like to embed the scripts now (if yes, then add your scripts to ~/.chat-script/scripts before submitting)? y/n: "))
            if user_embed:
                if user_embed[0] == "y" or user_embed[0] == "Y":
                    options.read()
                    embeddings.generate()
                    app.launch()
                elif user_embed[0] == "n" or user_embed[0] == "N":
                    options.read()
                    app.launch()
                else:
                    print("Input must be one of: y/n\n")
                    user_embed = None
    else:
        options.read()
        app.launch()

if __name__ == '__main__':
    init()