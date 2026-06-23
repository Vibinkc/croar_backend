import requests
from bs4 import BeautifulSoup


def debug_search(platform_name, site_domain, result_pattern, query, location=None):
    search_url = "https://duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    full_query = f'site:{site_domain} "{query}"'
    if location:
        full_query += f' "{location}"'

    print(f"DEBUG: Searching for: {full_query}")

    try:
        response = requests.get(search_url, params={"q": full_query}, headers=headers, timeout=10)
        print(f"DEBUG: Status Code: {response.status_code}")

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Check if we got results
            links = soup.find_all("a", class_="result__a")
            print(f"DEBUG: Found {len(links)} result links")

            for link in links:
                href = link.get("href", "")
                print(f"DEBUG: Result link: {href}")
                if result_pattern in href:
                    title = link.get_text()
                    print(f"DEBUG: Matching result: {title}")
        else:
            print(f"DEBUG: Response text snippet: {response.text[:500]}")

    except Exception as e:
        print(f"DEBUG: Exception: {e}")


if __name__ == "__main__":
    # Test LinkedIn
    debug_search("linkedin", "linkedin.com/in/", "linkedin.com/in/", "React Developer", "San Francisco")
