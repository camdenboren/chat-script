#!/usr/bin/env python

# Gradio UI leveraging eponymous function in response

import time
import gradio as gr
import response as r

app = gr.ChatInterface(
    r.response,
    chatbot=gr.Chatbot(
        show_copy_button=True, 
        bubble_full_width=False,
        height=500
    ),
    title="chat-script",
    description="Chat locally with text documents (scripts) of your choice with this simple python app.",
    analytics_enabled=False,
    additional_inputs=[]
).queue()
app.launch()