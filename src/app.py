# Gradio UI leveraging eponymous function in response

import os
import time
from configparser import ConfigParser
import gradio as gr
import response as r

# Directory and file names
config_file = "~/.config/chat-script/chat-script.ini"

# Set options
configuration = ConfigParser()
configuration.read(os.path.expanduser(config_file))
share = configuration.getboolean("APP", "share", fallback=False)
server_name = configuration.get("APP", "server_name", fallback="127.0.0.1")
server_port = configuration.getint("APP", "server_port", fallback=7860)
inbrowser = configuration.getboolean("APP", "inbrowser", fallback=True)

def app():
    """Launch app's Gradio UI"""
    r.c.set_vectorstore()
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
    app.launch(
        share=share, 
        server_name=server_name, 
        server_port=server_port,
        inbrowser=inbrowser
    )