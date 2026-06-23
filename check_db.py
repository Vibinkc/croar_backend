import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


def check():
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("MONGO_DB_NAME")]
    coll = db["candidate_profiles"]

    total = coll.count_documents({})
    print(f"Total profiles in DB: {total}")

    print("\n--- 10 NEWEST PROFILES ---")
    newest = list(coll.find().sort("_id", -1).limit(10))
    for p in newest:
        print(f"Name: {p.get('full_name')} | Email: {p.get('email')} | Platform: {p.get('platform')}")

    print("\n--- SEARCH TEST: 'Senior Frontend Developer' ---")
    # Simulate the chat_db query logic
    keywords = ["senior", "frontend", "developer"]
    query_filter = {
        "$or": [{"headline": {"$regex": k, "$options": "i"}} for k in keywords]
        + [{"skills": {"$regex": k, "$options": "i"}} for k in keywords]
    }

    matches = coll.count_documents(query_filter)
    print(f"Matches for keywords {keywords}: {matches}")

    results = list(coll.find(query_filter).sort("_id", -1).limit(5))
    for p in results:
        print(f"Match: {p.get('full_name')} | Email: {p.get('email')}")


if __name__ == "__main__":
    check()
