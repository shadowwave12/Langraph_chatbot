
import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

CONFIG = {"configurable": {"thread_id": "thread-1"}}

# Initialize chat history once per Streamlit session
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []


def extract_text(content):
    """Extract readable text from LangChain message content."""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict)
            and block.get("type") == "text"
        )

    return ""


#*****************************Main UI***************************
# Display all previous messages on every rerun
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Accept new user input
user_input = st.chat_input("Type here...")

if user_input:
    # Save and display the user message
    st.session_state["message_history"].append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # Stream and display the assistant response
    with st.chat_message("assistant"):

        def generate_response():
            for message_chunk, metadata in chatbot.stream(
                {
                    "messages": [
                        HumanMessage(content=user_input)
                    ]
                },
                config=CONFIG,
                stream_mode="messages",
            ):
                text = extract_text(message_chunk.content)

                if text:
                    yield text

        ai_message = st.write_stream(generate_response())

    # Save the complete response as a string
    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )
