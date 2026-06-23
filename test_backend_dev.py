import json

from dotenv import load_dotenv

from app.services.enterprise.sourcing.github import GitHubProvider

# Load environment variables (OXYLABS credentials)
load_dotenv()


def test_backend_search():
    provider = GitHubProvider()
    print("Searching for 'Backend Developer' on GitHub...")

    # Search for backend developers
    results = provider.search("backend developer", page_size=5)

    print(f"Found {len(results)} results.")

    for i, res in enumerate(results):
        print(f"\n--- Result {i + 1} ---")
        print(f"Name: {res['full_name']}")
        print(f"Profile: {res['profile_url']}")
        print(f"Email: {res['email']}")
        print(f"Company: {res['company']}")
        print(f"Location: {res['location']}")
        print(f"Followers: {res['followers']}")

    # Save first result to a file for inspection
    if results:
        with open("backend_dev_result.json", "w") as f:
            json.dump(results[0], f, indent=2)
        print("\nSaved first result to backend_dev_result.json")


if __name__ == "__main__":
    test_backend_search()
