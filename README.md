# chat-script

Chat locally with scripts (documents) of your choice with this simple python app.

Leverages Nix, Ollama, Langchain, ChromaDB, and Gradio to accomplish RAG (retrieval-augmented generation) on local LLMs with a basic UI.

<details>
<summary><b>Setup</b></summary>
<b>Important: Must install Ollama and flake-enabled Nix before running anything.</b>

Start Ollama server (second and third commands only need to be run if models have not already been installed):

    ollama serve
    ollama pull mistral
    ollama pull mxbai-embed-large

<i>Note: I recommend running Ollama as a system service to avoid needing to run 'ollama serve' every time I boot.</i>
</details>

<details>
<summary><b>Usage</b></summary>
Before any context can be used by the LLM, these context "scripts" must be added to ~/.chat-script/scripts

Executing the following will create this directory, generate embeddings (if desired), and run the app:

    nix run github:camdenboren/chat-script

Scripts can be reembeded at any time by executing the following:

    nix develop github:camdenboren/chat-script --command bash -c "python src/embeddings.py"

Now, the nix run command can be rerun to run this app normally (no local install needed, though it may be convenient for dedicated servers, etc.).

Access app at link: http://127.0.0.1:7860/

<i>*Note: Ollama must be running in the background in order for the app to actually get a response- see <b>Setup</b> for commands. It's also worthwhile to make sure the LLM is running on your GPU, otherwise responses are unbearably slow</i>
</details>

<details>
<summary><b>Advanced Usage</b></summary>
To adjust various options:

    git clone https://github.com/camdenboren/chat-script.git
    modify files in src as desired
    nix run /path/to/chat-script

Serve a public demo (builds upon immediately preceeding instructions):

    set 'share = True' in app.py
    nix run /path/to/chat-script
    curl {given CDN link} /path/to/download
    sudo cp /path/to/download/frpc_platform_arch_v0.2  /nix/store/.../gradio
    sudo chmod +x frpc_platform_arch_v0.2

Efficiently grab Youtube video transcripts

    Use this link to put video transcripts in ~/.chat-script/scripts: https://youtubechanneltranscripts.com/
    copy video title from freetube into search bar there
    For transcripts, made it through the video: Worlds Hardest One Set Leg Workout (MUSCLE GROWTH FAST)
</details>

<details>
<summary><b>ToDo</b></summary>

Priority
- [ ] Implement app configuration
- [ ] Add vectorstore indexing to avoid embeddings dupes
- [ ] Improve print_state functionality (reimplement previous RunnablePassthrough approach)
- [ ] Add few-shot prompting to improve citation formatting

Long-term
- [ ] Investigate routing options for settings ui
- [ ] Move to a more customizable UI via either gradio.Interface(), gradio.Blocks(), or a different framework like streamlit or flask
- [ ] Add button to call embeddings()
- [ ] Add dropdown to select available Ollama LLMs
</details>