# Gradio UI leveraging eponymous function in response

import time
import gradio as gr
import chain
import options
import response

def launch():
    """Launch app's Gradio UI"""
    chain.create()
    app = gr.ChatInterface(
        response.generate,
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
        share=options.options['app']['share'], 
        server_name=options.options['app']['server_name'], 
        server_port=options.options['app']['server_port'],
        inbrowser=options.options['app']['inbrowser']
    )