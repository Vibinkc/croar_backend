import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


def check_history():
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("MONGO_DB_NAME")]
    coll = db["chat_history"]

    count = coll.count_documents({})
    print(f"Total chat sessions in DB: {count}")

    sessions = list(coll.find().sort("updated_at", -1).limit(10))
    for s in sessions:
        print(f"Session: {s.get('title')} | ID: {s.get('session_id')} | Msgs: {len(s.get('messages', []))}")


if __name__ == "__main__":
    check_history()
