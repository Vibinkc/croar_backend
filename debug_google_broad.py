from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup


def test_broad_google_parse(query, site_domain, result_pattern):
    url = "https://www.google.com/search"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    params = {"q": f'site:{site_domain} "{query}"', "num": 10}

    print(f"DEBUG: Testing Broad Google for {query} with site:{site_domain}")
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"DEBUG: Status {response.status_code}")

        profiles = []
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            for link_el in soup.find_all("a"):
                href = link_el.get("href", "")
                if "/url?q=" in href:
                    href = parse_qs(urlparse(href).query).get("q", [href])[0]

                if result_pattern in href and "google.com" not in href:
                    print(f"DEBUG: Found link: {href}")
                    profiles.append(href)

        print(f"DEBUG: Final profiles count: {len(profiles)}")
        return profiles
    except Exception as e:
        print(f"DEBUG: Error {e}")


if __name__ == "__main__":
    test_broad_google_parse("Data Scientist", "linkedin.com/in/", "linkedin.com/in/")
