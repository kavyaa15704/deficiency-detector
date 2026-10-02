"""
Spoonacular recipe lookup, one function, easy to unit-test on its own.

Requires SPOONACULAR_API_KEY in a .env file at the project root.
"""
import os

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.spoonacular.com/recipes/complexSearch"
TIMEOUT_SECONDS = 8


def get_recipes(query: str, number: int = 3) -> list[dict]:
    """Return up to `number` recipes for a food/ingredient query.

    Each result: {"title": str, "image": str, "url": str}.
    Returns [] on any API error or missing key, so a Spoonacular outage
    never crashes the prediction flow - it just means no recipes that round.
    """
    api_key = os.getenv("SPOONACULAR_API_KEY")
    if not api_key:
        print("WARNING: SPOONACULAR_API_KEY not set in .env - skipping recipe lookup")
        return []

    params = {"query": query, "number": number, "apiKey": api_key}
    try:
        resp = requests.get(BASE_URL, params=params, timeout=TIMEOUT_SECONDS)
        resp.raise_for_status()
        results = resp.json().get("results", [])
    except requests.exceptions.RequestException as e:
        print(f"WARNING: Spoonacular request failed for '{query}': {e}")
        return []

    return [
        {
            "title": r.get("title", "Untitled"),
            "image": r.get("image", ""),
            "url": f"https://spoonacular.com/recipes/{r.get('title', '').replace(' ', '-')}-{r.get('id')}",
        }
        for r in results
    ]


if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "spinach"
    recipes = get_recipes(query)
    if not recipes:
        print(f"No recipes returned for '{query}' - check your API key and quota.")
    for r in recipes:
        print(f"- {r['title']}\n  {r['url']}")
