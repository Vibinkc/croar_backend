import json

from dotenv import load_dotenv

from app.services.enterprise.sourcing.github import GitHubProvider

load_dotenv()


def main():
    provider = GitHubProvider()
    print("Searching for 'smakosh'...")
    results = provider.search(query="smakosh", page=1, page_size=1)

    if results:
        # To avoid giant HTML output in terminal, we can write it to a file or truncate the HTML
        res = results[0]
        # Make a copy and truncate HTML for display
        display_res = res.copy()
        if "html" in display_res.get("raw_data", {}):
            html = display_res["raw_data"]["html"]
            display_res["raw_data"]["html"] = (
                f"HTML content length: {len(html)} chars. Preview: {html[:200]}..."
            )
        print(json.dumps(display_res, indent=2))

        # Save full JSON to a file so we have it
        with open("smakosh_output.json", "w", encoding="utf-8") as f:
            json.dump(results[0], f, indent=2, ensure_ascii=False)
        print("Full output saved to smakosh_output.json")
    else:
        print("No results found.")


if __name__ == "__main__":
    main()
