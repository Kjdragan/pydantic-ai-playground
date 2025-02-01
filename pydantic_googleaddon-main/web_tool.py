# pydantic_googleaddon/web_tool.py

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from urllib.parse import urlparse, quote_plus

class WebTool:
    DEBUG = True  # Class variable for debug mode

    @classmethod
    def log_debug(cls, message):
        if cls.DEBUG:
            print(f"DEBUG: {message}")

    def __init__(self, num_results: int = 10, max_tokens: int = 4096):
        self.num_results = num_results
        self.max_tokens = max_tokens
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        self.log_debug("WebTool initialized")

    def search(self, query: str) -> List[Dict[str, Any]]:
        self.log_debug(f"Performing web search for: {query}")
        search_results = self._perform_web_search(query)
        filtered_results = self._filter_search_results(search_results)
        deduplicated_results = self._remove_duplicates(filtered_results)
        self.log_debug(f"Found {len(deduplicated_results)} unique results")
        return deduplicated_results[:self.num_results]

    def _perform_web_search(self, query: str) -> List[Dict[str, Any]]:
        encoded_query = quote_plus(query)
        search_url = f"https://www.google.com/search?q={encoded_query}&num={self.num_results * 2}&hl=en"
        self.log_debug(f"Search URL: {search_url}")
        
        try:
            self.log_debug("Sending GET request to Google")
            response = requests.get(search_url, headers=self.headers, timeout=10)
            self.log_debug(f"Response status code: {response.status_code}")
            response.raise_for_status()
            
            # Check if we got the anti-bot page
            if 'Our systems have detected unusual traffic' in response.text:
                self.log_debug("Anti-bot detection triggered")
                raise Exception("Google's anti-bot detection was triggered. Please try again later or use a different approach.")
            
            self.log_debug("Parsing HTML with BeautifulSoup")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            self.log_debug("Searching for result divs")
            search_results = []

            # Debug: Print the HTML structure
            with open('debug_output.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            self.log_debug("Saved HTML response to debug_output.html")
            
            # Find all search result containers - using more specific selectors
            main_results = soup.select('div.g')
            
            for result in main_results:
                try:
                    # Find title and URL
                    link_elem = result.select_one('a')
                    if not link_elem:
                        continue
                        
                    url = link_elem.get('href', '')
                    if not url or not url.startswith('http'):
                        continue
                    
                    # Get title from h3
                    title_elem = result.select_one('h3')
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    
                    # Get description
                    desc_elem = result.select_one('div.VwiC3b, div.IsZvec')
                    description = desc_elem.get_text(strip=True) if desc_elem else ''
                    
                    if title and url:
                        self.log_debug(f"Found result: Title: {title[:30]}..., URL: {url[:30]}...")
                        search_results.append({
                            'title': title,
                            'description': description,
                            'url': url
                        })
                except Exception as e:
                    self.log_debug(f"Error processing result: {str(e)}")
                    continue
            
            self.log_debug(f"Successfully retrieved {len(search_results)} search results for query: {query}")
            return search_results
            
        except requests.RequestException as e:
            self.log_debug(f"Error performing search: {str(e)}")
            raise  # Re-raise the exception after logging

    def _filter_search_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        filtered = [result for result in results if result['description'] and result['title'] != 'No title' and result['url'].startswith('https://')]
        self.log_debug(f"Filtered to {len(filtered)} results")
        return filtered

    def _remove_duplicates(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen_urls = set()
        unique_results = []
        for result in results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        self.log_debug(f"Removed duplicates, left with {len(unique_results)} results")
        return unique_results

    def get_web_content(self, url: str) -> str:
        self.log_debug(f"Fetching content from: {url}")
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            content = text[:self.max_tokens]
            self.log_debug(f"Retrieved {len(content)} characters of content")
            return content
        except requests.RequestException as e:
            self.log_debug(f"Error retrieving content from {url}: {str(e)}")
            raise  # Re-raise the exception after logging

    def is_url(self, text: str) -> bool:
        try:
            result = urlparse(text)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def _clean_url(self, url: str) -> str:
        url = url.rstrip(')')  # Remove trailing parenthesis if present
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url  # Add https:// if missing
        return url
