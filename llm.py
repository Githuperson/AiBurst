import streamlit as st
import requests
import json
import time
from search import web_search

# 🌐 Unified OpenAI-compatible router endpoint
API_URL = "https://router.huggingface.co/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {st.secrets['HF_TOKEN']}",
    "Content-Type": "application/json"
}

def query_custom_model(prompt: str) -> str:
    """
    Queries Hugging Face's unified provider router using the OpenAI chat format.
    """
    payload = {
        "model": "Qwen/Qwen2.5-7B-Instruct:fastest", 
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 512,
        "temperature": 0.7
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response_json = response.json()
        
        # 1. Parse successful response
        if "choices" in response_json and len(response_json["choices"]) > 0:
            return response_json["choices"][0]["message"]["content"].strip()
        
        # 2. Safely parse error strings or dictionaries
        if "error" in response_json:
            err = response_json["error"]
            if isinstance(err, dict):
                return f"❌ Router Error: {err.get('message', err)}"
            return f"❌ Router Error: {err}"
            
        return "⚠️ Received an unparseable response format from the router."

    except requests.exceptions.Timeout:
        return "❌ Connection timed out. The provider router took too long to respond."
    except Exception as e:
        return f"❌ Network error: {str(e)}"
def stream_chat_with_qwen(user_message: str, history: list):
    """
    Orchestration layer. Automatically fires a web search unless the 
    message is a simple greeting or casual chit-chat.
    """
    # 1. Define a quick list of common casual greetings
    greetings = ["hello", "hi", "hey", "sup", "yo", "greetings", "good morning", "good afternoon", "good evening", "howdy"]
    
    # Clean up the user's message to check it accurately
    clean_message = user_message.strip().lower().replace("?", "").replace("!", "")
    
    context = ""
    
    # 2. Only search if it's NOT a basic greeting
    if clean_message in greetings:
        context = "" # Skip search for simple hellos
    else:
        with st.spinner("Searching the web for current data..."):
            try:
                context = web_search(user_message, max_results=3)
            except Exception:
                context = ""  # Safe fallback if search fails

    # 3. Build the unified system prompt structure
    base_prompt = ""
    if context:
        base_prompt += f"System: Use the following verified real-time web context to answer the user's query:\n{context}\n\n"
    
    base_prompt += f"User: {user_message}\nAssistant:"
    
    # 4. Request inference answer
    model_reply = query_custom_model(base_prompt)
    
    if not model_reply or not isinstance(model_reply, str):
        model_reply = "⚠️ The inference model returned an empty response. Please try sending your message again."
    
    # 5. Stream output back to the interface chunk-by-chunk
    words = model_reply.split(" ")
    for i, word in enumerate(words):
        yield " ".join(words[:i+1]) + " "
        time.sleep(0.02)
