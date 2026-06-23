import os

from dotenv import load_dotenv
from pymongo import MongoClient

from app.services.enterprise.sourcing.github import GitHubProvider

# Load credentials
load_dotenv()


def store_top_candidates():
    # Initialize GitHub Provider
    provider = GitHubProvider()

    # Initialize MongoDB
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("MONGO_DB_NAME", "croar_sourcing")

    print(f"Connecting to MongoDB at {mongo_uri}...")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db["candidate_profiles"]

    query = "Senior Frontend Developer"
    target_count = 10
    found_candidates = []
    page = 1

    print(f"Searching for {target_count} candidates with emails for query: '{query}'...")

    while len(found_candidates) < target_count and page <= 5:
        print(f"Searching page {page}...")
        results = provider.search(query, page=page, page_size=15)

        for res in results:
            if res.get("email") and len(found_candidates) < target_count:
                # Add a few extra metadata fields for better chat experience
                res["skills"] = ["Frontend", "React", "JavaScript", "Senior"]
                if res.get("headline"):
                    # Simple skill extraction from headline
                    for s in ["TypeScript", "Vue", "Angular", "Next.js", "Node", "CSS", "HTML"]:
                        if s.lower() in res["headline"].lower():
                            res["skills"].append(s)

                found_candidates.append(res)
                print(f"Found candidate {len(found_candidates)}: {res['full_name']} ({res['email']})")

            if len(found_candidates) >= target_count:
                break

        page += 1

    if found_candidates:
        print(f"\nStoring {len(found_candidates)} candidates in MongoDB...")
        # Use update_one with upsert to avoid duplicates
        for cand in found_candidates:
            collection.update_one({"profile_url": cand["profile_url"]}, {"$set": cand}, upsert=True)
        print("Successfully stored candidates in MongoDB collection 'candidate_profiles'.")
    else:
        print("No candidates with emails found.")


if __name__ == "__main__":
    store_top_candidates()
