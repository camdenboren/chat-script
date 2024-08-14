# Returns response w/ citations from RAG-enabled LLM based on user question passed from app ui

import os
import time
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from gradio import Request
import chain
import options

# Directory and file names
scripts_directory = "~/.chat-script/scripts"

# Calculate length of scripts_dir name for citation formatting later
scripts_dir_len = len(os.path.expanduser(scripts_directory))
if scripts_directory[-1] != "/":
    scripts_dir_len += 1

# Message sent when unsafe question is asked and options.options['chain']['moderate'] = True
unsafe_response = "Your question is unsafe, so no response will be provided."
    
def format_context(context):
    """Formats and yields context passed to LLM in human-readable format"""
    if options.options['response']['print_state']:
        print("Context: ", context, sep="")
    formatted_context = "Relevant Sources (some may not have been used): "
    index = 0
    yield "\n\n"
    while(index < len(context)):
        formatted_context += "[" + str(index+1) + "] " + context[index].metadata["source"][scripts_dir_len:]
        for chunks in formatted_context.split():
            yield chunks + " "
            if((index == 0) and (chunks == "used):")):
                yield "\n"
            time.sleep(options.options['response']['context_stream_delay'])
        yield "\n"
        formatted_context = ""
        index += 1

def convert_session_history(history):
    """Workaround for converting Gradio history to Langchain-compatible chat_history.
    Separates chat_history by user and lets Clear on Gradio UI do its job"""
    global session_history
    session_history = ChatMessageHistory()

    # Remove unsafe messages from history if applicable
    if options.options['chain']['moderate']:
        for msgs in history:
            if (msgs[1] == unsafe_response + " "):
                history.remove(msgs)
    
    # Trim history before converting to langchain format
    if len(history) > options.options['response']['max_history']:
        history = history[-options.options['response']['max_history']:]
    for msgs in history:
        session_history.add_user_message(msgs[0])
        session_history.add_ai_message(msgs[1].split("\n\nRelevant Sources")[0])

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Manage chat history"""
    return session_history

def inspect(state):
    """Print state between runnables and pass it on (includes: input, chat_history)"""
    if options.options['response']['print_state']:
        print("State: ", state, sep="")
    return state

def generate(question,history,request: Request):
    """Checks question for safety (if applicable) then creates RAG + history chain w/ local LLM and streams chain's text response"""
    if request and options.options['response']['print_state']:
        print("\nIP address of user: ", request.client.host, sep="")
    allow_response = True
    if options.options['chain']['moderate']:
        check_question = chain.moderation_chain.invoke(question)
        allow_response = (check_question[2:6] == "safe")
    if allow_response:
        convert_session_history(history)
        
        # Define retrieval chain w/ history
        rag_history_chain = RunnableWithMessageHistory(
            RunnableLambda(inspect) | chain.rag_chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
        # Old approach for including context in state - investigate this further to prevent separate context printing
        #retrieve_docs = (lambda x: x["input"]) | retriever
        #chain = RunnablePassthrough.assign(context=retrieve_docs).assign(answer=rag_chain_from_docs)

        # Return/yield response and formatted context (if applicable) as a text stream
        result = rag_history_chain.stream({"input": question},config={"configurable": {"session_id": "unused"}})
        response_stream = ""
        context = None
        for chunks in result:
            answer_chunks = chunks.get("answer")
            get_context = chunks.get("context")
            if(answer_chunks):
                response_stream += answer_chunks
            if(get_context):
                context = get_context
            yield response_stream
        if context:
            formatted_context = format_context(context)
            for context_chunks in formatted_context:
                response_stream += context_chunks
                yield response_stream
    else:
        print("Unsafe question: \'", question, "\'", sep="")
        response_stream = ""
        for chunks in unsafe_response.split():
            response_stream += chunks + " "
            yield response_stream
            time.sleep(options.options['response']['context_stream_delay'])