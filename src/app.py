#!/usr/bin/env python

# Gradio UI leveraging eponymous function in response

import time
import gradio as gr
import response as r
import embeddings as e
import os

# Directory names
scripts_directory = "~/.chat-script/scripts"
embeddings_directory = "~/.chat-script/embeddings"

# Misc options
share = False

def init():
    """Create directories and embed scripts if needed, otw run app()"""
    if (not os.path.exists(os.path.expanduser(scripts_directory))) and (not os.path.exists(os.path.expanduser(embeddings_directory))):
        os.makedirs(os.path.expanduser(scripts_directory))
        os.makedirs(os.path.expanduser(embeddings_directory))
        print("\nCreated scripts_directory at: " + scripts_directory + "and embeddings_directory at: " + embeddings_directory)
        user_embed = None
        while not user_embed:
            user_embed = str(input("Would you like to embed the scripts now (if yes, then add your scripts to ~/.chat-script/scripts before submitting)? y/n: "))
            if user_embed:
                if user_embed[0] == "y" or user_embed[0] == "Y":
                    e.embeddings()
                elif user_embed[0] == "n" or user_embed[0] == "N":
                    app()
                else:
                    print("Input must be one of: y/n\n")
                user_embed = None
    else:
        app()

def app():
    """Launch app's Gradio UI"""
    app = gr.ChatInterface(
        r.response,
        chatbot=gr.Chatbot(
            show_copy_button=True, 
            bubble_full_width=False,
            scale=1
        ),
        fill_height=True,
        title="chat-script",
        description="Chat locally with scripts (documents) of your choice with this simple python app.",
        analytics_enabled=False,
        additional_inputs=[]
    ).queue()
    app.launch(share=share)

if __name__ == '__main__':
    init()