"""Entry point that ensures necessary config and scripts are setup before handing off to app.py"""

# SPDX-FileCopyrightText: 2024 Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
from src import app, embeddings, options

# Directory and file names
SCRIPTS_DIR = "~/.chat-script/scripts"
EMBED_DIR = "~/.chat-script/embeddings"
CONFIG_DIR = "~/.config/chat-script"
CONFIG_FILE = f"{CONFIG_DIR}/chat-script.ini"


def main():
    """Create directories and embed scripts if needed, otw run options.read() and app.launch()"""
    if not os.path.exists(os.path.expanduser(CONFIG_FILE)):
        if not os.path.exists(os.path.expanduser(CONFIG_DIR)):
            os.makedirs(os.path.expanduser(CONFIG_DIR))
            options.create()
        else:
            options.create()
        if os.path.exists(os.path.expanduser(SCRIPTS_DIR)):
            options.read()
            app.launch()
    elif not os.path.exists(os.path.expanduser(SCRIPTS_DIR)):
        os.makedirs(os.path.expanduser(SCRIPTS_DIR))
        print("\nCreated SCRIPTS_DIR at: " + SCRIPTS_DIR)
        user_embed = None
        while not user_embed:
            user_embed = str(
                input(
                    """Would you like to embed the scripts now (if yes, then add your 
                scripts to ~/.chat-script/scripts before submitting)? y/n: """
                )
            )
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


if __name__ == "__main__":
    sys.exit(main())
