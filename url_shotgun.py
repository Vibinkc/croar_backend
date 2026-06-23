import requests


def shotgun():
    base = "http://localhost:8000"
    variations = [
        "/api/v1/enterprise/sourcing/chat/sessions",
        "/api/v1/enterprise/sourcing/chat/sessions/",
        "/api/v1/enterprise/enterprise/sourcing/chat/sessions",
        "/enterprise/sourcing/chat/sessions",
        "/sourcing/chat/sessions",
        "/api/v1/enterprise/chat/sessions",
        "/api/v1/sourcing/chat/sessions",
    ]

    for v in variations:
        url = base + v
        try:
            r = requests.get(url)
            print(f"GET {v} -> {r.status_code}")
        except Exception:
            print(f"GET {v} -> FAILED")


if __name__ == "__main__":
    shotgun()
