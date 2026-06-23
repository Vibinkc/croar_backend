import asyncio

import httpx


async def test_dashboard_stats():
    base_url = "http://localhost:8000/api/v1"

    # 1. Login
    login_data = {"username": "admin@appxcess.com", "password": "Admin@123"}

    async with httpx.AsyncClient() as client:
        try:
            print(f"Logging in as {login_data['username']}...")
            response = await client.post(f"{base_url}/auth/token", data=login_data)
            if response.status_code != 200:
                print(f"Login failed: {response.text}")
                return

            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("Login successful.")

            # 2. Get Stats
            print("Fetching dashboard stats...")
            stats_response = await client.get(f"{base_url}/enterprise/dashboard/stats", headers=headers)
            if stats_response.status_code == 200:
                print("Dashboard Stats Success:")
                print(stats_response.json())
            else:
                print(f"Stats request failed: {stats_response.status_code}")
                print(stats_response.text)

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_dashboard_stats())
