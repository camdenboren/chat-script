# Gradio UI leveraging eponymous function in response

import time
import gradio as gr
import response as r
import os
from configparser import ConfigParser

configuration = ConfigParser()

# Directory names
config_directory = "~/.config/chat-script"
config_file = config_directory + "/chat-script.ini"

# Misc options
if not os.path.exists(os.path.expanduser(config_directory)):
    share = False
else:
    configuration.read(os.path.expanduser(config_file))
    share = configuration.getboolean("APP","share")

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