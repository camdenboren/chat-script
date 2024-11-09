"""Gradio UI leveraging eponymous function in response"""

# SPDX-FileCopyrightText: 2024 Camden Boren
#
# SPDX-License-Identifier: GPL-3.0-or-later

import gradio as gr
from src import chain, options, response


def opt(option_name):
    """Syntactic sugar for retrieving options"""
    return options.OPTIONS["app"][option_name]


def launch():
    """Launch app's Gradio UI"""
    chain.create()
    app = gr.ChatInterface(
        response.generate,
        chatbot=gr.Chatbot(
            show_copy_button=True,
            bubble_full_width=False,
            scale=1,
        ),
        type="tuples",
        fill_height=True,
        title="chat-script",
        theme="gradio/monochrome",
        analytics_enabled=False,
        additional_inputs=[],
    ).queue()
    app.launch(
        share=opt("share"),
        server_name=opt("server_name"),
        server_port=opt("server_port"),
        inbrowser=opt("inbrowser"),
    )
