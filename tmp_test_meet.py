import asyncio
import os
import sys

# add backend path
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta

from app.services.enterprise.interview_service import generate_google_meet_link


async def main():
    try:
        link = await generate_google_meet_link(
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(minutes=30),
            candidate_email="test1@example.com",
            interviewer_email="test2@example.com",
            job_title="Test Software Engineer",
        )
        print("GENERATED LINK:", link)
    except Exception as e:
        print("EXCEPTION:", str(e))


if __name__ == "__main__":
    asyncio.run(main())
