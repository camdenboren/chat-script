<div align="center">
<img src='docs/img/chat-script.png' height=auto width=400px>

![Static Badge](https://img.shields.io/badge/Version-1.1-blue?style=for-the-badge)
![Static Badge](https://img.shields.io/badge/Platforms-Linux,_macOS-forestgreen?style=for-the-badge)
![Static Badge](https://img.shields.io/badge/Coverage-92%25-forestgreen?style=for-the-badge)
![Static Badge](https://img.shields.io/badge/Powered_by_Nix-grey?logo=nixOS&logoColor=white&logoSize=auto&style=for-the-badge)

Chat with your documents using any Ollama LLM with this simple python app<br>
Docs deployed at https://camdenboren.github.io/chat-script<br>
_Docs cover options, architecture, and reference_

| Features     |
| ------------ |
| RAG-Fusion   |
| Streaming    |
| Chat History |
| Citations    |
| Moderation   |

</div>

## Setup

**Must install Ollama before running anything**

Start Ollama server (second and third commands only need to be run if models have not already been installed, fourth only applies if moderate is set to True)

    ollama serve
    ollama pull mistral
    ollama pull mxbai-embed-large
    ollama pull llama-guard3:1b

_I recommend running Ollama as a system service to avoid needing to run 'ollama serve' every time I boot_

## Usage

Before any context can be used by the LLM, these context "scripts" must be added to ~/.chat-script/scripts

### Nix

**Must install flake-enabled Nix before running**

Executing the following will create this directory, generate embeddings (if desired), and run the app

    nix run github:camdenboren/chat-script

Scripts can be reembedded at any time by renaming/removing the scripts directory and rerunning the above command, or by executing the following (if you don't want to run the app)

    nix develop github:camdenboren/chat-script --command bash -c "python -m src.embeddings"

### Non-Nix

**Must install Python 3.12.7 and Node.js v20.18.0 before running**\
_On Linux, you'll also need to install build-essential, libdbus-glib-1-dev, and libgirepository1.0-dev\
On macOS, you'll also need dbus_

Clone this repo (or download prefered release)

    git clone https://github.com/camdenboren/chat-script.git

Navigate to directory, then create and activate venv (optional)

    mkdir .venv
    python -m venv .venv
    source .venv/bin/activate

Next, install dependencies

    pip install -r requirements.txt

Finally, executing the following will create this directory, generate embeddings (if desired), and run the app

    python -m src

Scripts can be reembedded at any time by renaming/removing the scripts directory and rerunning the above command, or by executing the following (if you don't want to run the app)

    python -m src.embeddings

## Advanced Usage

To edit the code itself

    git clone https://github.com/camdenboren/chat-script.git

Modify files in src as desired (and add new files to setup.py and stage), then

    nix run /path/to/chat-script

## ToDo

### Contributions welcome

- [x] Look into RAG-fusion for improving distance-based retrieval performance
- [x] Look into other splitting functions due to weirdness from book pdfs
- [x] Add moderation sub-option for system alerts (Linux-only)
- [ ] Move to 'messages' for gradio as 'tuples' will be removed soon
- [ ] Add vectorstore indexing to avoid embeddings dupes
- [ ] Add support for non-text documents (relevant packages below)
- [ ] Add tool-call or few-shot prompting to improve citation formatting
- [ ] Eliminate globals
- [ ] Reimplement previous RunnablePassthrough approach for print_state
- [ ] Add logging

### Relevant pkgs:

_Needed for PDF processing - should work once paddlepaddle is updated - also need to rm loader_cls in embeddings()_

- unstructured
- emoji
- iso-639
- langdetect
- pillow-heif
- unstructured-inference
- beautifulsoup4 (seems unnecessary)

## License

[GPLv3](COPYING)
