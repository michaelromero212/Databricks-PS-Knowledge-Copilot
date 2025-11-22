import requests
from bs4 import BeautifulSoup
from typing import Optional

class Scraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Databricks-PS-Knowledge-Copilot/1.0'
        }

    def fetch_page(self, url: str) -> Optional[str]:
        """Fetches the HTML content of a page."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_text(self, html_content: str) -> str:
        """Extracts text from HTML content."""
        if not html_content:
            return ""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()

        text = soup.get_text(separator='\n')
        return text
