from dotenv import load_dotenv
import os       
from tavily import TavilyClient 

load_dotenv()
# TAVILY_API_KEY = os.getenv("Ttvly-dev-IM7RKJSxWRzJtPReZia53AzZi6VMR6Wj")

# tavily_client = TavilyClient(TAVILY_API_KEY)
tavily_client = TavilyClient("Ttvly-dev-IM7RKJSxWRzJtPReZia53AzZi6VMR6Wj")


def web_response(question):
    web_search_results = ""
    if tavily_client:
        try:
            search_results = tavily_client.search(question)
            if search_results and search_results.get("results"):
                results_content = [result["content"] for result in search_results["results"] if result.get("content")]
                web_search_results = "\n".join(results_content)
            else:
                web_search_results = "No web search results found."
        except Exception as e:
            web_search_results = f"Web search is currently unavailable. Error: {e}"
    else:
        web_search_results = "Tavily API key not set. Web search disabled."
    return web_search_results