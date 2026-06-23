import json

from dotenv import load_dotenv

from app.services.enterprise.sourcing.github import GitHubProvider

load_dotenv()


def test_github_provider():
    provider = GitHubProvider()
    print("Searching for 'developer'...")
    results = provider.search(query="developer", page=1, page_size=2)

    if results:
        print(f"Found {len(results)} results!")
        print("First result:")
        print(json.dumps(results[0], indent=2))
    else:
        print("No results found.")


if __name__ == "__main__":
    test_github_provider()
