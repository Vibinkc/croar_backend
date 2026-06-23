import requests
from bs4 import BeautifulSoup


def test_google(query, site_domain):
    url = f'https://www.google.com/search?q=site:{site_domain} "{query}"'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    print(f"DEBUG: Testing Google for {query}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"DEBUG: Status {response.status_code}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a")
            found = 0
            for link in links:
                href = link.get("href", "")
                if site_domain in href:
                    found += 1
            print(f"DEBUG: Found {found} potential links")
    except Exception as e:
        print(f"DEBUG: Error {e}")


if __name__ == "__main__":
    test_google("React Developer", "linkedin.com/in/")
