import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


def add_user_vibin():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    mongo_db_name = os.getenv("MONGO_DB_NAME", "croar_sourcing")

    client = MongoClient(mongo_uri)
    db = client[mongo_db_name]
    coll = db["candidate_profiles"]

    vibin_profile = {
        "full_name": "Vibin KC",
        "email": "vibi@appxcess.com",
        "headline": "Senior Frontend Developer",
        "location": "India",
        "platform": "github",
        "profile_url": "https://github.com/vibin-kc",
        "avatar_url": "https://avatars.githubusercontent.com/u/vibin?v=4",
        "company": "Appxcess",
        "skills": ["React", "Next.js", "TypeScript", "Tailwind CSS", "JavaScript"],
        "public_repos": 45,
        "followers": 120,
        "following": 50,
        "hireable": True,
        "social_links": [
            {"platform": "github", "url": "https://github.com/vibin-kc"},
            {"platform": "linkedin", "url": "https://linkedin.com/in/vibin-kc"},
        ],
        "raw_data": {},
    }

    # Use update_one with upsert to avoid duplicates and ensure it's "fresh"
    coll.delete_one({"email": "vibi@appxcess.com"})  # Remove if exists to make it "first" in newest sort
    coll.insert_one(vibin_profile)

    print(f"Successfully added {vibin_profile['full_name']} to the database as {vibin_profile['headline']}.")


if __name__ == "__main__":
    add_user_vibin()
