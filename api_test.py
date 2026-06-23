import os

import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
response = requests.get(f"{BACKEND_URL}/api/v1/enterprise/applications/", params={"job_id": "ALL"})
if response.status_code == 200:
    for app in response.json():
        if app.get("candidate", {}).get("full_name") == "vibin":
            print(f"App ID: {app['id']}")
            print(f"AI Match Score: {app.get('ai_match_score')}")
            print(f"AI Interview Score: {app.get('ai_interview_score')}")
            print(f"Aptitude Score: {app.get('aptitude_score')}")
            print("---")
else:
    print(f"Failed: {response.status_code}")
