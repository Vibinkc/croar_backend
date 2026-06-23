import requests
from bs4 import BeautifulSoup


def debug_search_lite(platform_name, site_domain, result_pattern, query, location=None):
    search_url = "https://duckduckgo.com/lite/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    full_query = f'site:{site_domain} "{query}"'
    if location:
        full_query += f' "{location}"'

    print(f"DEBUG LITE: Searching for: {full_query}")

    try:
        response = requests.get(search_url, params={"q": full_query}, headers=headers, timeout=10)
        print(f"DEBUG LITE: Status Code: {response.status_code}")

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # In Lite mode, results are in tables
            links = soup.find_all("a", class_="result-link")
            print(f"DEBUG LITE: Found {len(links)} result links")

            for link in links:
                href = link.get("href", "")
                print(f"DEBUG LITE: Result link: {href}")
                if result_pattern in href:
                    title = link.get_text()
                    print(f"DEBUG LITE: Matching result: {title}")
        else:
            print(f"DEBUG LITE: Response text snippet: {response.text[:500]}")

    except Exception as e:
        print(f"DEBUG LITE: Exception: {e}")


if __name__ == "__main__":
    debug_search_lite("linkedin", "linkedin.com/in/", "linkedin.com/in/", "React Developer", "San Francisco")
