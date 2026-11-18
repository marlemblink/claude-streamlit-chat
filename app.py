
import streamlit as st
import anthropic
import os
from dotenv import load_dotenv

# env variables
load_dotenv(override=True)

api_key = os.getenv("ANTHROPIC_API_KEY")

# page configuration
st.set_page_config(
    page_title="Nihao - Claude AI Chat"
)

st.title("Nihao - Claude AI Chat")

# verify API key
if not api_key:
    st.error("API Key not found in .env")
    st.stop()

# create client for Anthropic
client = anthropic.Anthropic(api_key=api_key)

# lateral configuration
st.sidebar.header("Settings")

if st.sidebar.button("Clear Conversation"):
    st.session_state.messages = []
    st.rerun()

model = st.sidebar.selectbox(
    "Select Model",
    [
        "claude-sonnet-4-5",
        "claude-haiku-4-5",
        "claude-opus-4-5"
    ]
)

# Effort configuration
effort = st.sidebar.selectbox(
    "Effort Configuration",
    ["low", "medium", "high"],
    index=1
)

if model == "claude-opus-4-5":
    st.sidebar.info("Effort configuration available.")
else:
    st.sidebar.info("Effort is available only with Claude Opus 4.5.")

# Thinking Option
thinking = st.sidebar.checkbox(
    "Enable Thinking",
    value=False
)

# System Instruction
system_prompt = st.sidebar.text_area(
    "System Instruction",
    "You are a helpful AI assistant."
)

# Historial
if "messages" not in st.session_state:
    st.session_state.messages = []

# show conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# user input
prompt = st.chat_input("Write your message...")

if prompt:

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.write(prompt)

    try:
        with st.chat_message("assistant"):
            with st.spinner("Claude is thinking..."):
                
                # Build request dynamically
                request_params = {
                    "model": model,
                    "max_tokens": 4096,
                    "system": system_prompt,
                    "messages": st.session_state.messages #message's history
                }
                
                # Thinking Configuration
                if thinking:
                    request_params["thinking"] = {
                        "type": "enabled",
                        "budget_tokens": 2048
                    }

                # Effort Configuration
                if model == "claude-opus-4-5":
                    request_params["output_config"] = {
                        "effort": effort
                    }

                # Send request to Claude
                response = client.messages.create(**request_params)

                # Get Claude response
                answer = "\n".join(
                    block.text
                    for block in response.content
                    if block.type == "text"
                )

                st.write(answer)


        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

    except anthropic.AuthenticationError:
        st.error("Authentication error: Check your Anthropic API Key.")

    except anthropic.APIError as e:
        st.error(f"API Error: {e}")
