import asyncio
import uuid
from datetime import date, timedelta

import httpx

BACKEND_URL = "http://localhost:8000"


async def test_launch_survey() -> None:
    # 1. Get a template ID
    async with httpx.AsyncClient() as client:
        # We need a token. I'll try to find one or just assume an agent exists.
        # Actually, I can just try to call the endpoint and see the 401/500 behavior.
        # But to see the 500, I need to be authenticated.

        # Let's try to find an agent in the DB to get his ID and company_id if needed,
        # but the API requires a JWT.
        print("This script requires a valid JWT token to test the 500 error.")
        print("Attempting to call /launch WITHOUT token to see if it's 401 or 500.")

        payload = {
            "template_id": str(uuid.uuid4()),
            "name": "Test Survey",
            "start_date": str(date.today()),
            "end_date": str(date.today() + timedelta(days=7)),
            "target_group": "ALL",
        }

        try:
            res = await client.post(f"{BACKEND_URL}/api/v1/enterprise/surveys/launch", json=payload)
            print(f"Response Status: {res.status_code}")
            print(f"Response Body: {res.text}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_launch_survey())
