import json

import requests

HASHNODE_URL = "https://gql.hashnode.com"

# SearchUser has a 'user' nested field — introspect it
print("=== introspect SearchUser type ===")
introspect = """
{
  __type(name: "SearchUser") {
    fields { name type { name kind ofType { name kind } } }
  }
}
"""
r = requests.post(
    HASHNODE_URL, json={"query": introspect}, headers={"Content-Type": "application/json"}, timeout=10
)
print(json.dumps(r.json(), indent=2))
