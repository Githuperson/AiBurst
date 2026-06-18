import streamlit as st
from ddgs import DDGS
import requests
from bs4 import BeautifulSoup

def scrape_website(url: str) -> str:
    """
    Visits a URL and extracts raw paragraph text from the page.
    """
    try:
        # Pretend to be a regular browser so the website doesn't block the request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return ""
            
        # Parse the webpage HTML structure
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Pull all the paragraphs (<p> tags) from the article body
        paragraphs = soup.find_all('p')
        text_content = [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 20]
        
        # Take the top 4-5 substantial paragraphs so we don't exceed model limits
        full_article_snippet = " ".join(text_content[:5])
        return full_article_snippet
        
    except Exception as e:
        print(f"⚠️ Scraping failed for {url}: {str(e)}")
        return ""

def web_search(query: str, max_results: int = 3) -> str:
    """
    Searches the web, grabs top URLs, and deeply scrapes their full content.
    """
    try:
        with DDGS() as ddgs:
            # Gather search links
            results = list(ddgs.text(query, max_results=max_results))
            
        if not results:
            return ""
            
        context_list = []
        for r in results:
            title = r.get("title", "No Title")
            url = r.get("href", r.get("url", ""))
            
            # 🌐 Go the extra mile: visit and scrape the full page text if a URL exists
            scraped_text = ""
            if url:
                scraped_text = scrape_website(url)
                
            # Fallback to the basic snippet if scraping fails or returns blank
            body = scraped_text if scraped_text else r.get("body", "")
            
            context_list.append(f"Title: {title}\nURL: {url}\nContent: {body}\n---")
            
        return "\n\n".join(context_list)
        
    except Exception as e:
        print(f"⚠️ Search layer exception: {str(e)}")
        return ""
