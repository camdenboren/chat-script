# chat-scripts

Chat locally with text documents (scripts) of your choice with this simple python app.

Leverages Nix, Ollama, Langchain, ChromaDB, and Gradio to accomplish RAG on local LLMs with a basic UI.

<details>
<summary><b>Setup</b></summary>

<b>Important: Must install Ollama and flake-enabled Nix before running anything.</b>

Clone repo:

    git clone https://github.com/camdenboren/chat-scripts.git

Enter development environment (cd to repo first):

    nix develop

Start Ollama server:

    ollama serve
    ollama run dolphin-mistral

</details>

<details>
<summary><b>Usage</b></summary>

Use this link to put video transcripts in ./transcripts: https://youtubechanneltranscripts.com/<br>
copy video title from freetube into search bar there<br>
For transcripts, made it through the video: Worlds Hardest One Set Leg Workout (MUSCLE GROWTH FAST)

Refresh document/script embeddings: 

    nix develop
    ./embeddings.py
    Add documents and rerun if nothing happens
    
<i>*Note: runs an embedding model on cpu so it takes a while</i>

Run app: 

    exit
    nix run

<i>*Note: Ollama must be running in the background in order for the app to actually get a response- see <b>Setup</b> for commands. It's also worthwhile to make sure the LLM is running on your GPU, otherwise responses are unbearably slow</i>

Access app at link: http://127.0.0.1:7860/

Interact like normal

To set 'share=True' in app.launch()

    curl {given CDN link}
    sudo cp frpc_platform_arch_v0.2  /nix/store/.../gradio
    sudo chmod +x frpc_platform_arch_v0.2
    
</details>

<details>
<summary><b>ToDo</b></summary>

- [ ] Move to a more customizable UI via either gradio.Interface(), gradio.Blocks(), or a different framework like streamlit or flask
- [ ] Add button to call embeddings()
- [ ] Add dropdown to select available Ollama LLMs

</details>