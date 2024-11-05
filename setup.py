"""Declare app name, ver, scripts, and entry point"""

# SPDX-FileCopyrightText: 2024 Camden Boren
#
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import setup

setup(
    name="chat-script",
    version="0.1",
    packages=["src"],
    scripts=[
        "src/app.py",
        "src/chain.py",
        "src/embeddings.py",
        "src/multi_retriever.py",
        "src/options.py",
        "src/response.py",
    ],
    entry_points={"console_scripts": ["chat-script = src.__main__:main"]},
)
