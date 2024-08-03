# chat-script

Chat locally with scripts (documents) of your choice with this simple python app that features: 
- Citations
- Moderation
- Chat History

This is accomplished by implementing RAG on local LLMs via:
- Ollama
- Langchain
- ChromaDB
- Gradio

Package and development environment powered by Nix

<details>
<summary><b>Setup</b></summary>
<b>Important: Must install Ollama and flake-enabled Nix before running anything.</b>

Start Ollama server (second and third commands only need to be run if models have not already been installed, fourth only applies if moderate is set to True):

    ollama serve
    ollama pull mistral
    ollama pull mxbai-embed-large
    ollama pull xe/llamaguard3

<i>Note: I recommend running Ollama as a system service to avoid needing to run 'ollama serve' every time I boot.</i>
</details>

<details>
<summary><b>Usage</b></summary>
Before any context can be used by the LLM, these context "scripts" must be added to ~/.chat-script/scripts

Executing the following will create this directory, generate embeddings (if desired), and run the app:

    nix run github:camdenboren/chat-script

Access app at link: http://127.0.0.1:7860/

Scripts can be reembedded at any time by renaming/removing the scripts directory and rerunning:

    nix run github:camdenboren/chat-script

Or by executing the following (if you don't want to run the app):

    nix develop github:camdenboren/chat-script --command bash -c "python src/embeddings.py"

<i>*Note: Ollama must be running in the background in order for the app to actually get a response- see <b>Setup</b> for commands. It's also worthwhile to make sure the LLMs are running on your GPU, otherwise responses are unbearably slow</i>
</details>

<details>
<summary><b>Advanced Usage</b></summary>
To adjust various options, edit values in:

    ~/.config/chat-script/chat-script.ini

To edit the code itself:

    git clone https://github.com/camdenboren/chat-script.git
    modify files in src as desired
    nix run /path/to/chat-script

Efficiently grab Youtube video transcripts

    Use this link to put video transcripts in ~/.chat-script/scripts: https://youtubechanneltranscripts.com/
    copy video title from freetube into search bar there
    For transcripts, made it through the video: Worlds Hardest One Set Leg Workout (MUSCLE GROWTH FAST)
</details>

<details>
<summary><b>ToDo</b></summary>

Priority
- [ ] Add vectorstore indexing to avoid embeddings dupes
- [ ] Add few-shot prompting to improve citation formatting
- [ ] Look into RAG-fusion for improving distance-based retrieval performance
- [ ] Look into other splitting functions due to weirdness from book pdfs
- [ ] Improve print_state functionality (reimplement previous RunnablePassthrough approach)

Long-term
- [ ] Investigate routing options for settings ui
- [ ] Move to a more customizable UI via either gradio.Interface(), gradio.Blocks(), or a different framework like streamlit or flask
- [ ] Add button to call embeddings()
- [ ] Add dropdown to select available Ollama LLMs
- [ ] Improve documentation
</details>