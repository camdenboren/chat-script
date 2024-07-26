#!/usr/bin/env python

# Gradio UI leveraging eponymous function in response

import time
import gradio as gr
import response as r
import os

# Directory names
scripts_directory = "~/.chat-script/scripts"

def check_scripts_dir():
    """Create scripts_directory if needed"""
    if not os.path.exists(os.path.expanduser(scripts_directory)):
        os.makedirs(os.path.expanduser(scripts_directory))
        print("\nCreated scripts_directory at: " + scripts_directory + ". Add your scripts there and run 'nix develop github:camdenboren/chat-script --command bash -c \"python src/embeddings.py\" to embed them.")
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
    app.launch()

if __name__ == '__main__':
    check_scripts_dir()