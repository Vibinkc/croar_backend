import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


def find_our_candidates():
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("MONGO_DB_NAME")]
    coll = db["candidate_profiles"]

    names_to_find = ["teffcode", "webeli", "frontender-training", "smakosh", "erikaperciliano"]

    print("--- SEARCHING FOR OUR SPECIFIC SAVED CANDIDATES ---")
    for name in names_to_find:
        # Use regex to find by name or login
        res = coll.find_one(
            {
                "$or": [
                    {"full_name": {"$regex": name, "$options": "i"}},
                    {"profile_url": {"$regex": name, "$options": "i"}},
                ]
            }
        )

        if res:
            print(f"✅ FOUND: {name} | Email: {res.get('email')} | ID: {res.get('_id')}")
        else:
            print(f"❌ NOT FOUND: {name}")


if __name__ == "__main__":
    find_our_candidates()
