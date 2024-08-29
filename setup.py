from setuptools import setup

setup(
    name='chat-script',
    version='0.1',
    packages=["src"],
    scripts=[
        "src/app.py",
        "src/chain.py",
        "src/embeddings.py",
        "src/options.py",
        "src/response.py"
    ],
    entry_points={
        "console_scripts": [
            "chatbot-util = src.__main__:main"
        ]
    }
)