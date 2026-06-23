from dotenv import load_dotenv

from app.services.enterprise.sourcing.github import GitHubProvider

load_dotenv()


def verify_search_emails():
    provider = GitHubProvider()
    query = "senior frontend developer"
    print(f"Searching for '{query}'...")

    results = provider.search(query, page_size=10)
    print(f"Found {len(results)} results.\n")

    for i, res in enumerate(results):
        status = "FOUND" if res["email"] else "MISSING"
        print(f"[{i + 1}] {res['full_name']} - Email: {res['email']} {status}")

    emails_found = len([r for r in results if r["email"]])
    print(f"\nSummary: Found emails for {emails_found}/{len(results)} profiles.")


if __name__ == "__main__":
    verify_search_emails()
