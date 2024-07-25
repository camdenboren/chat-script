#!/usr/bin/env python

# Gradio UI leveraging eponymous function in response

import time
import gradio as gr
import response as r
import os

# Directory names
document_directory = "~/.chat-script/scripts"

# Create document_directory if needed 
def check_doc_dir():
    # Create document_directory if needed 
    if not os.path.exists(os.path.expanduser(document_directory)):
        os.makedirs(os.path.expanduser(document_directory))
        print("\nCreated document_directory at: " + document_directory + ". Add your documents there and run 'nix develop github:camdenboren/chat-script --command bash -c \"python src/embeddings.py\" to embed them.")
    else:
        app()

# Launch app's Gradio UI
def app():
    app = gr.ChatInterface(
        r.response,
        chatbot=gr.Chatbot(
            show_copy_button=True, 
            bubble_full_width=False,
            scale=1
        ),
        fill_height=True,
        title="chat-script",
        description="Chat locally with text documents (scripts) of your choice with this simple python app.",
        analytics_enabled=False,
        additional_inputs=[]
    ).queue()
    app.launch()

if __name__ == '__main__':
    check_doc_dir()