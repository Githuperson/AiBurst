import streamlit as st
# 🔄 Directly importing DDGS from the newly configured 'ddgs' package
from ddgs import DDGS

def web_search(query: str, max_results: int = 3) -> str:
    """
    Searches the web using the modern DDGS library and aggregates snippets.
    """
    try:
        # Opening the connection with the strict context manager
        with DDGS() as ddgs:
            # max_results must be a keyword argument in this version!
            results = list(ddgs.text(query, max_results=max_results))
            
        if not results:
            return ""
            
        # Compile titles and snippets into context blocks
        context_list = []
        for r in results:
            title = r.get("title", "No Title")
            body = r.get("body", "")  # Uses the modern 'body' key for snippets
            context_list.append(f"Title: {title}\nSnippet: {body}\n---")
            
        return "\n\n".join(context_list)
        
    except Exception as e:
        print(f"⚠️ Search layer exception: {str(e)}")
        return ""
