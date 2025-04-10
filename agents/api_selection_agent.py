import os
import requests
import time
import feedparser
import datetime
from .memory_manager import MemoryManager

class APISelectionAgent:
    """
    Fetches external data using the Google Custom Search API, NASA API, and also queries arXiv for research papers.
    Uses robust error handling, retry logic, and includes a simple in-memory cache.
    """
    def __init__(self, memory: MemoryManager, max_retries=2):
        self.memory = memory
        self.max_retries = max_retries
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "YOUR_GOOGLE_API_KEY")
        self.google_cx = os.getenv("GOOGLE_CX", "YOUR_GOOGLE_CX")
        self.google_endpoint = "https://www.googleapis.com/customsearch/v1"
        self.nasa_api_key = os.getenv("NASA_API_KEY", "YOUR_NASA_API_KEY")
        self.nasa_endpoint = "https://api.nasa.gov/planetary/apod"
        self.cache = {}

    def fetch_external_data(self, query: str) -> dict:
        self.memory.log_event(f"[APISelectionAgent] Processing external data for: '{query}'")
        # Update caching to store the full dictionary result.
        if query in self.cache:
            self.memory.log_event("[APISelectionAgent] Cache hit! Returning cached data.")
            cached_data = self.cache[query]
            self.memory.store_data("external_data", cached_data)
            return cached_data

        space_keywords = ["nasa", "space", "astronomy", "planet", "cosmos", "asteroid", "galaxy"]
        if any(keyword in query.lower() for keyword in space_keywords):
            data = self._fetch_from_nasa(query)
        else:
            data = self._fetch_from_google(query)
        research_data = self._fetch_from_arxiv(query)
        # Log the number of advancements found for debugging
        self.memory.log_event(f"[APISelectionAgent] Found {len(research_data)} advancements from arXiv.")
        result = {"summary": data, "recent_advancements": research_data}
        self.cache[query] = result
        self.memory.log_event("[APISelectionAgent] Cached the new result.")
        self.memory.store_data("external_data", result)
        return result

    def _fetch_from_google(self, query: str) -> str:
        self.memory.log_event("[APISelectionAgent] Querying Google Custom Search API.")
        params = {
            "q": query,
            "key": self.google_api_key,
            "cx": self.google_cx,
            "num": 5
        }
        for attempt in range(self.max_retries):
            response = requests.get(self.google_endpoint, params=params)
            if response.status_code == 200:
                search_results = response.json()
                if "items" in search_results:
                    top_results = search_results["items"]
                    urls = [res.get("link") for res in top_results]
                    self.memory.store_data("external_urls", urls)
                    results = "\n".join([
                        f"Title: {res.get('title')}\nLink: {res.get('link')}\nSnippet: {res.get('snippet')}\n"
                        for res in top_results
                    ])
                    return results
                else:
                    return "No web results found."
            else:
                self.memory.log_event(f"[APISelectionAgent] Google API attempt {attempt+1} failed with status {response.status_code}")
                time.sleep(1)
        return f"Error: Google Search API request failed after {self.max_retries} attempts."

    def _fetch_from_nasa(self, query: str) -> str:
        self.memory.log_event("[APISelectionAgent] Querying NASA API (APOD).")
        params = {
            "api_key": self.nasa_api_key,
            "hd": True
        }
        for attempt in range(self.max_retries):
            response = requests.get(self.nasa_endpoint, params=params)
            if response.status_code == 200:
                data = response.json()
                title = data.get("title", "No title provided.")
                explanation = data.get("explanation", "No explanation available.")
                result = f"NASA APOD\nTitle: {title}\nExplanation: {explanation}\n"
                return result
            else:
                self.memory.log_event(f"[APISelectionAgent] NASA API attempt {attempt+1} failed with status {response.status_code}")
                time.sleep(1)
        return f"Error: NASA API request failed after {self.max_retries} attempts."

    def _fetch_from_arxiv(self, query: str) -> list:
        self.memory.log_event("[APISelectionAgent] Querying arXiv API for research papers.")
        url = "http://export.arxiv.org/api/query"
        current_year = datetime.datetime.now().year
        threshold_year = current_year - 5  # Only include papers from the last 5 years
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": 10,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }
        # Retry logic for the arXiv API call
        for attempt in range(self.max_retries):
            response = requests.get(url, params=params)
            if response.status_code == 200:
                break
            else:
                self.memory.log_event(f"[APISelectionAgent] arXiv API attempt {attempt+1} failed with status {response.status_code}")
                time.sleep(1)
        else:
            self.memory.log_event("[APISelectionAgent] arXiv API request failed after retries")
            return []

        feed = feedparser.parse(response.text)
        papers = []
        for entry in feed.entries:
            published_str = entry.get("published", "")
            try:
                published_date = datetime.datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%SZ")
                published_year = published_date.year
            except Exception as e:
                self.memory.log_event(f"[APISelectionAgent] Error parsing published date '{published_str}': {e}")
                published_date = None
                published_year = 0
            if published_year >= threshold_year:
                pointer = {
                    "title": entry.get("title", "No Title").strip(),
                    "summary": entry.get("summary", "No summary available.").strip(),
                    "year": published_year,
                    "published": published_str,
                    "link": entry.get("link", ""),
                    # Optionally, precompute a parsed_date for easier sorting:
                    "parsed_date": time.strptime(published_str, "%Y-%m-%dT%H:%M:%SZ") if published_date else time.gmtime(0)
                }
                papers.append(pointer)
        return papers
