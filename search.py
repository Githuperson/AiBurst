from duckduckgo_search import DDGS

def web_search(query, max_results=3):    
    try:        
        output = []        
        with DDGS() as ddgs:            
            results = ddgs.text(query, max_results=max_results)            
            for r in results:                
                title = r.get("title", "")                
                body = r.get("body", "")                
                url = r.get("href", "")                
                output.append(                    
                    f"Title: {title}\n"                    
                    f"Snippet: {body}\n"                    
                    f"Source: {url}\n"                
                )        
        return "\n".join(output)    
    except Exception as e:        
        return f"Search failed: {e}"