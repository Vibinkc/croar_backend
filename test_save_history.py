import uuid

import requests


def test_save():
    url = "http://localhost:8000/api/v1/enterprise/sourcing/chat/sessions"
    session_id = str(uuid.uuid4())
    data = {
        "session_id": session_id,
        "title": "Final Correction Test",
        "messages": [
            {"role": "user", "content": "Checking corrected path", "timestamp": "2024-04-30T10:00:00Z"},
            {"role": "ai", "content": "Corrected path should work!", "timestamp": "2024-04-30T10:00:05Z"},
        ],
    }

    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_save()
