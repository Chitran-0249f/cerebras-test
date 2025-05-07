import os
import streamlit as st
from cerebras.cloud.sdk import Cerebras

# Set page config
st.set_page_config(
    page_title="Active Learning Tutor",
    page_icon="🎓",
    layout="centered"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "learning_state" not in st.session_state:
    st.session_state.learning_state = {
        "topic": None,
        "current_phase": "initial",  # initial, diagnostic, teaching, assessment
        "knowledge_level": None,
        "learning_style": None
    }
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Initialize Cerebras client
@st.cache_resource
def get_cerebras_client():
    return Cerebras(api_key=os.environ.get("CEREBRAS_API_KEY"))

def get_system_prompt(learning_state):
    if learning_state["current_phase"] == "initial":
        return """You are an intelligent, adaptive AI tutor. Your first task is to understand what the user wants to learn.
        Ask them what topic they want to learn about and their learning goals or background in the topic.
        Be friendly and encouraging."""
    
    elif learning_state["current_phase"] == "diagnostic":
        return f"""You are an intelligent, adaptive AI tutor. The user wants to learn about {learning_state['topic']}.
        Ask 2-3 diagnostic questions to assess their current knowledge level.
        Make the questions specific and relevant to the topic.
        After each answer, provide brief feedback and adjust your next question based on their response."""
    
    elif learning_state["current_phase"] == "teaching":
        return f"""You are an intelligent, adaptive AI tutor teaching {learning_state['topic']}.
        Follow this active learning loop:
        1. Ask a concept-checking question
        2. Based on the answer, provide feedback
        3. Offer a clear explanation or analogy
        4. Ask a follow-up question to reinforce understanding
        
        Keep explanations concise and engaging. Use examples when possible.
        Adapt your teaching style based on the user's responses.
        Current knowledge level: {learning_state['knowledge_level']}"""
    
    return """You are an intelligent, adaptive AI tutor. Continue the active learning process,
    maintaining engagement and checking for understanding."""


def process_response(response, learning_state):
    # Update learning state based on the conversation
    if learning_state["current_phase"] == "initial" and "topic" not in response.lower():
        learning_state["current_phase"] = "diagnostic"
        learning_state["topic"] = response
    
    elif learning_state["current_phase"] == "diagnostic" and len(st.session_state.messages) >= 4:
        learning_state["current_phase"] = "teaching"
        # Analyze responses to determine knowledge level
        learning_state["knowledge_level"] = "beginner"  # This could be made more sophisticated
    
    return learning_state

# App title and description
st.title("🎓 Active Learning Tutor")
st.markdown("Learn anything through interactive, personalized tutoring")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response from Cerebras
    try:
        client = get_cerebras_client()
        
        # Prepare conversation history with system prompt
        messages = [
            {"role": "system", "content": get_system_prompt(st.session_state.learning_state)},
            *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        ]
        
        response = client.chat.completions.create(
            messages=messages,
            model="llama-4-scout-17b-16e-instruct",
        )
        
        # Extract and display assistant's response
        assistant_response = response.choices[0].message.content
        
        # Update learning state based on the conversation
        st.session_state.learning_state = process_response(assistant_response, st.session_state.learning_state)
        
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
    This is an active learning tutor that adapts to your learning style and pace.
    
    The tutor will:
    1. Ask what you want to learn
    2. Assess your current knowledge
    3. Provide personalized lessons
    4. Check your understanding
    5. Adjust the teaching approach based on your responses
    """)
    
    # Display current learning state
    st.markdown("### Current Learning State")
    st.json(st.session_state.learning_state)
    
    # Add a reset button
    if st.button("Reset Session"):
        st.session_state.messages = []
        st.session_state.learning_state = {
            "topic": None,
            "current_phase": "initial",
            "knowledge_level": None,
            "learning_style": None
        }
        st.session_state.conversation_history = []
        st.rerun() 
