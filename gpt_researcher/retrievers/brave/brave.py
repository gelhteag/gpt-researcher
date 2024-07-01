# Brave Search Retriever

# libraries
import os
import json
import logging
import requests
from typing import List, Dict, Optional



class BraveSearch:
    """
    Brave Search Retriever
    """
    def __init__(self, query: str, max_results: int = 7):
        """
        Initializes the BraveSearch object
        Args:
            query: search query
        """
        self.query = query
        self.api_key = self.get_api_key()
        self.base_url = "https://api.search.brave.com/res/v1/"

    def get_api_key(self) -> str:
        """
        Gets the Brave API key
        Returns: Brave API key
        """
        try:
            api_key = os.environ["BRAVE_API_KEY"]
        except KeyError:
            raise Exception("Brave API key not found. Please set the BRAVE_API_KEY environment variable.")
        return api_key

    def _prepare_headers(self) -> Dict[str, str]:
        """Prepare the common headers required for the API requests."""
        return {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }

    def _get(self, params: Optional[Dict[str, str]] = None) -> requests.Response:
        """GET request method."""
        headers = self._prepare_headers()
        req = requests.PreparedRequest()
        req.prepare_url(self.base_url + "web/search", params)
        response = requests.get(req.url, headers=headers)
        return response

    def search(self,max_results=7) -> List[Dict[str, str]]:
        """
        Searches the query
        Returns: list of search results
        """
        logging.debug(f"Searching with query '{self.query}' and max results '{max_results}'...")
       
        params = {
            "q": self.query,
            "count": min(max_results, 20),  # Ensuring count does not exceed API limits
            "safesearch": "strict",
            "locale": "en-GB"
        }

        resp = self._get(params=params)

        # Preprocess the results
        if not resp.ok:
            logging.error(f"API request failed with status code {resp.status_code}")
            return []
        try:
            search_results = resp.json()
            logging.debug("Search Results Response: %s", search_results)  # Debugging line
        except json.JSONDecodeError:
            logging.error("Failed to parse response")
            return []
        if search_results is None:
            return []

        # Correctly parse the results from the "web" key
        results = search_results.get("web", {}).get("results", [])
        if not results:
            logging.debug("No results found")
        search_results_list = []

        # Normalize the results to match the format of the other search APIs
        for count, result in enumerate(results, 1):
            if "youtube.com" in result.get("url", ""):
                continue
            search_result = {
                "count": count,
                "title": result.get("title", ""),
                "href": result.get("url", ""),
                "body": result.get("description", ""),
            }
            search_results_list.append(search_result)

        return search_results_list