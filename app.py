import streamlit as st
import pymongo
from datetime import datetime
from llm import stream_chat_with_qwen

# 1. This MUST be the absolute first Streamlit command!
st.set_page_config(page_title="AiBurst - Llama 3.2", page_icon="⚡", layout="centered")

# 2. Now you can safely initialize your database functions and hooks
@st.cache_resource
def init_mongodb():
    try:
        client = pymongo.MongoClient(st.secrets["MONGO_URI"])
        db = client["aiburst_database"]
        return db["chat_logs"]
    except Exception as e:
        st.warning(f"Database logging is offline: {str(e)}")
        return None

db_logs = init_mongodb()

# 3. Rest of your UI elements follow below...
st.title("⚡ AiBurst Chat System")
st.caption("Powered by a custom fine-tuned Llama 3.2 model with real-time web search integration.")

# Initialize Conversational Session State History arrays
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past chat elements dynamically on application rebuilds
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capture User Chat Inputs
if prompt := st.chat_input("Ask your custom model anything..."):
    # 1. Display User Message on Screen
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Process Assistant Streams
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # We explicitly pass BOTH arguments to match your new llm.py generator signature
        for chunk in stream_chat_with_qwen(prompt, st.session_state.messages):
            full_response = chunk
            response_placeholder.markdown(full_response + "▌")
            
        # Strip trailing block caret once stream finishes
        response_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # 3. Log Interactions to MongoDB Securely 
    if db_logs is not None:
        log_payload = {
            "timestamp": datetime.utcnow(),
            "user_prompt": prompt,
            "model_response": full_response
        }
        try:
            db_logs.insert_one(log_payload)
        except Exception:
            pass  # Fails silently to prevent user UI disruptions if DB blips