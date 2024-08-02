# Gradio UI leveraging eponymous function in response

import time
import gradio as gr
import response as r
import os
from configparser import ConfigParser

# Directory and file names
config_file = "~/.config/chat-script/chat-script.ini"

# Set options
configuration = ConfigParser()
configuration.read(os.path.expanduser(config_file))
share = configuration.getboolean("APP", "share", fallback=False)

def app():
    """Launch app's Gradio UI"""
    r.set_vectorstore()
    app = gr.ChatInterface(
        r.response,
        chatbot=gr.Chatbot(
            show_copy_button=True, 
            bubble_full_width=False,
            scale=1
        ),
        fill_height=True,
        title="chat-script",
        analytics_enabled=False,
        additional_inputs=[]
    ).queue()
    app.launch(share=share)