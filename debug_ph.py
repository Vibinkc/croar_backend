import json

import requests


def test_product_hunt_api(query):
    token = "O8lsLThQFMk5EGUE4FE2SoKqjhnUP3hVzww6-xKJSds"
    url = "https://api.producthunt.com/v2/api/graphql"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Let's try a simpler query first to see if we get ANY posts
    gql_query = """
    query {
      posts(first: 5) {
        edges {
          node {
            name
            makers {
              name
              username
            }
          }
        }
      }
    }
    """

    print("DEBUG: Testing Product Hunt API...")
    try:
        response = requests.post(url, headers=headers, json={"query": gql_query}, timeout=15)
        print(f"DEBUG: Status {response.status_code}")
        data = response.json()
        print(f"DEBUG: Data: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"DEBUG: Error: {e}")


if __name__ == "__main__":
    test_product_hunt_api("frontend")
