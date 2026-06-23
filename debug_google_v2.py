from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup


def test_full_google_parse(query, site_domain, result_pattern):
    url = "https://www.google.com/search"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    params = {"q": f'site:{site_domain} "{query}"', "num": 10}

    print(f"DEBUG: Testing Google for {query} with site:{site_domain}")
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"DEBUG: Status {response.status_code}")

        profiles = []
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Check for generic result containers
            results = (
                soup.find_all("div", class_="g")
                or soup.find_all("div", class_="tF2Cxc")
                or soup.find_all("div", class_="yuRUbf")
            )
            print(f"DEBUG: Found {len(results)} raw result divs")

            # If nothing found, try finding ALL links and their parents
            if not results:
                print("DEBUG: No result divs found, trying broader search")
                all_links = soup.find_all("a")
                for link in all_links:
                    href = link.get("href", "")
                    if "/url?q=" in href:
                        href = parse_qs(urlparse(href).query).get("q", [href])[0]
                    if result_pattern in href:
                        print(f"DEBUG: Found link in broad search: {href}")

            for res in results:
                link_el = res.find("a")
                if not link_el:
                    continue

                href = link_el.get("href", "")
                if "/url?q=" in href:
                    href = parse_qs(urlparse(href).query).get("q", [href])[0]

                print(f"DEBUG: Checking href: {href}")
                if result_pattern in href:
                    title_el = res.find("h3")
                    title = title_el.get_text() if title_el else "No Title"
                    print(f"DEBUG: Match found! Title: {title}")
                    profiles.append({"href": href, "title": title})

        print(f"DEBUG: Final profiles count: {len(profiles)}")
        return profiles
    except Exception as e:
        print(f"DEBUG: Error {e}")


if __name__ == "__main__":
    test_full_google_parse("Data Scientist", "linkedin.com/in/", "linkedin.com/in/")
