"""Debug script: print raw responses from Hashnode GraphQL and Gravatar REST.

Run from backend/: python debug_hashnode_gravatar.py
"""

import hashlib
import json

import requests

HASHNODE_URL = "https://gql.hashnode.com"

# ─── 1. Hashnode: introspect available query fields ───────────────────────────
print("\n" + "=" * 60)
print("HASHNODE — introspect top-level Query fields")
print("=" * 60)

introspect_gql = """
{
  __schema {
    queryType {
      fields {
        name
        args { name type { name kind ofType { name kind } } }
      }
    }
  }
}
"""
r = requests.post(
    HASHNODE_URL, json={"query": introspect_gql}, headers={"Content-Type": "application/json"}, timeout=15
)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    fields = data.get("data", {}).get("__schema", {}).get("queryType", {}).get("fields", [])
    for f in fields:
        print(f"  query: {f['name']}")
else:
    print("RAW:", r.text[:500])

# ─── 2. Hashnode: try searchPosts query (v3 schema) ───────────────────────────
print("\n" + "=" * 60)
print("HASHNODE — try 'searchPosts' query (v3)")
print("=" * 60)

search_gql = """
query SearchPosts($query: String!, $first: Int!) {
  searchPosts(query: $query, first: $first) {
    edges {
      node {
        title
        brief
        url
        author {
          username
          name
          tagline
        }
      }
    }
  }
}
"""
r2 = requests.post(
    HASHNODE_URL,
    json={"query": search_gql, "variables": {"query": "react", "first": 5}},
    headers={"Content-Type": "application/json"},
    timeout=15,
)
print(f"Status: {r2.status_code}")
print(json.dumps(r2.json(), indent=2)[:2000])

# ─── 3. Hashnode: try tag query ───────────────────────────────────────────────
print("\n" + "=" * 60)
print("HASHNODE — try 'tag' query")
print("=" * 60)

tag_gql = """
query TagPosts($slug: String!) {
  tag(slug: $slug) {
    name
    postsCount
    posts(first: 5) {
      edges {
        node {
          title
          url
          author {
            username
            name
            tagline
          }
        }
      }
    }
  }
}
"""
r3 = requests.post(
    HASHNODE_URL,
    json={"query": tag_gql, "variables": {"slug": "react"}},
    headers={"Content-Type": "application/json"},
    timeout=15,
)
print(f"Status: {r3.status_code}")
print(json.dumps(r3.json(), indent=2)[:2000])

# ─── 4. Gravatar: direct hash lookup (known test hash) ────────────────────────
print("\n" + "=" * 60)
print("GRAVATAR — REST v3 direct profile lookup (test email)")
print("=" * 60)

# Gravatar's own test email
test_email = "iamcelinedesigns@gmail.com"
h = hashlib.sha256(test_email.lower().strip().encode()).hexdigest()
url = f"https://api.gravatar.com/v3/profiles/{h}"
r4 = requests.get(url, headers={"Accept": "application/json", "User-Agent": "Croar-Debug/1.0"}, timeout=10)
print(f"Email: {test_email}  Hash: {h[:16]}...")
print(f"Status: {r4.status_code}")
print(json.dumps(r4.json(), indent=2)[:2000] if r4.status_code == 200 else r4.text[:500])

# ─── 5. Gravatar: old v1 API (XML / JSON) fallback ────────────────────────────
print("\n" + "=" * 60)
print("GRAVATAR — legacy v1 JSON profile")
print("=" * 60)

import hashlib as _hl

md5_hash = _hl.md5(test_email.lower().strip().encode()).hexdigest()
r5 = requests.get(
    f"https://www.gravatar.com/{md5_hash}.json", headers={"User-Agent": "Croar-Debug/1.0"}, timeout=10
)
print(f"Status: {r5.status_code}")
print(json.dumps(r5.json(), indent=2)[:2000] if r5.status_code == 200 else r5.text[:500])
