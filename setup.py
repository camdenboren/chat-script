#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='chat-script',
      version='0.1',
      # Modules to import from other scripts:
      packages=find_packages(),
      # Executables
      scripts=[
        "src/app.py", 
        "src/response.py", 
        "src/embeddings.py"
      ]
     )