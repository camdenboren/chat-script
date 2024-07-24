# chat-scripts

Chat locally with scripts (documents) of your choice with this simple python app.

Leverages Nix, Ollama, Langchain, ChromaDB, and Gradio to accomplish RAG (retrieval-augmented generation) on local LLMs with a basic UI.

<details>
<summary><b>Setup</b></summary>
<b>Important: Must install Ollama and flake-enabled Nix before running anything.</b>

Start Ollama server (second command only needs to be run if dolphin-mistral has not already been installed):

    ollama serve
    ollama run dolphin-mistral

<i>Note: I recommend running Ollama as a system service to avoid needing to run 'ollama serve' every time I boot.</i>

An optional setup step is to manually create the directory:

    ~/.chat-script

With the subfolders:

    ~/.chat-script/embeddings
    ~/.chat-script/transcripts

This allows you to prepare your transcripts before installing anything, but the folder creation itself is done automatically by the first 'nix run' command in the 'Usage' section.
</details>

<details>
<summary><b>Usage</b></summary>
Before any context can be used by the LLM, these context "scripts" must be added to ~/.chat-script/transcripts

Executing the following will create this directory:

    nix run github:camdenboren/chat-script

Once you add your scripts, run the following to generate their associated embeddings:

    nix develop github:camdenboren/chat-script --command bash -c ./embeddings.py

Now, the nix run command can be rerun to run this app normally (no local install needed, though it may be convenient for dedicated servers, etc.).

Access app at link: http://127.0.0.1:7860/

<i>*Note: Ollama must be running in the background in order for the app to actually get a response- see <b>Setup</b> for commands. It's also worthwhile to make sure the LLM is running on your GPU, otherwise responses are unbearably slow</i>
</details>

<details>
<summary><b>Advanced Usage</b></summary>
To set 'share=True' in app.launch()

    git clone github:camdenboren/chat-script.git
    cd chat-script
    modify app.py to include 'share=True'
    nix run .
    curl {given CDN link}
    sudo cp frpc_platform_arch_v0.2  /nix/store/.../gradio
    sudo chmod +x frpc_platform_arch_v0.2

Efficiently grab Youtube video transcripts

    Use this link to put video transcripts in ./transcripts: https://youtubechanneltranscripts.com/
    copy video title from freetube into search bar there
    For transcripts, made it through the video: Worlds Hardest One Set Leg Workout (MUSCLE GROWTH FAST)
</details>

<details>
<summary><b>ToDo</b></summary>

- [ ] Move to a more customizable UI via either gradio.Interface(), gradio.Blocks(), or a different framework like streamlit or flask
- [ ] Add button to call embeddings()
- [ ] Add dropdown to select available Ollama LLMs
</details>