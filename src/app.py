# Gradio UI leveraging eponymous function in response

import time
import gradio as gr
from options import options
from response import response
from chain import create_chain

def app():
    """Launch app's Gradio UI"""
    create_chain()
    app = gr.ChatInterface(
        response,
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
        share=options['app']['share'], 
        server_name=options['app']['server_name'], 
        server_port=options['app']['server_port'],
        inbrowser=options['app']['inbrowser']
    )