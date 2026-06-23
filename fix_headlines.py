import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


def fix():
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("MONGO_DB_NAME")]
    coll = db["candidate_profiles"]

    # Update only the ones we just added from GitHub that have null headlines
    result = coll.update_many(
        {"headline": None, "platform": "github"}, {"$set": {"headline": "Senior Frontend Developer"}}
    )
    print(
        f"Successfully updated {result.modified_count} profiles with the 'Senior Frontend Developer' headline."
    )


if __name__ == "__main__":
    fix()
