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
    # Using ':fastest' lets HF automatically route to Groq, Sambanova, Together, etc.
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
        
        # Parse OpenAI chat format out of the unified provider response
        if "choices" in response_json and len(response_json["choices"]) > 0:
            return response_json["choices"][0]["message"]["content"].strip()
        
        if "error" in response_json:
            return f"❌ Router Error: {response_json['error'].get('message', response_json['error'])}"
            
        return "⚠️ Received an unparseable response format from the router."

    except requests.exceptions.Timeout:
        return "❌ Connection timed out. The provider router took too long to respond."
    except Exception as e:
        return f"❌ Network error: {str(e)}"

def stream_chat_with_qwen(user_message: str, history: list):
    """
    Main orchestral layer called by app.py. Always runs a web search 
    to provide the model with real-time background context.
    """
    # 1. Always run the web search
    with st.spinner("Searching the web for current data..."):
        try:
            context = web_search(user_message, max_results=3)
        except Exception:
            context = "" # Fallback if search fails or times out

    # 2. Build the final prompt cleanly
    base_prompt = ""
    if context:
        # We add a strong system instruction so the model knows this is live web data
        base_prompt += f"System: Use the following verified real-time web context to answer the user's query:\n{context}\n\n"
    
    base_prompt += f"User: {user_message}\nAssistant:"
    
    model_reply = query_custom_model(base_prompt)
    
    if not model_reply or not isinstance(model_reply, str):
        model_reply = "⚠️ The inference model returned an empty response. Please try sending your message again."
    
    words = model_reply.split(" ")
    for i, word in enumerate(words):
        yield " ".join(words[:i+1]) + " "
        time.sleep(0.02)
