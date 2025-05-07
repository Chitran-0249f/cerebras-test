import os
import streamlit as st
from cerebras.cloud.sdk import Cerebras

# Set page config
st.set_page_config(
    page_title="Cerebras Chat",
    page_icon="🤖",
    layout="centered"
)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize Cerebras client
@st.cache_resource
def get_cerebras_client():
    return Cerebras(api_key="csk-6vj4yxx4vwkywwnhtvy8rwhvxfmkr4dpj2y8ncnp8je28394")

# App title and description
st.title("🤖 Cerebras Chat")
st.markdown("Chat with Cerebras' Llama-4-Scout-17B model")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response from Cerebras
    try:
        client = get_cerebras_client()
        response = client.chat.completions.create(
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            model="llama-4-scout-17b-16e-instruct",
        )
        
        # Extract and display assistant's response
        assistant_response = response.choices[0].message.content
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(assistant_response)
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please make sure your CEREBRAS_API_KEY is set in the environment variables.")

# Add a sidebar with information
with st.sidebar:
    st.markdown("### About")
    st.markdown("""
    This chat application uses Cerebras' Llama-4-Scout-17B model for generating responses.
    
    Make sure to set your CEREBRAS_API_KEY as an environment variable before running the app.
    """) 