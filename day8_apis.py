# Day 8 — REST API Practice
import requests
import json

print("===== DAY 8: REST API PRACTICE =====\n")

# PART 1 — Simple GET Request
print("--- PART 1: Simple GET Request ---")

response = requests.get("https://jsonplaceholder.typicode.com/posts/1")

print(f"Status Code: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"Response Data: {response.json()}")

# PART 2 — Reading response data
print("\n--- PART 2: Reading Response Data ---")

response = requests.get("https://jsonplaceholder.typicode.com/posts/1")
data = response.json()

print(f"Post ID: {data['id']}")
print(f"User ID: {data['userId']}")
print(f"Title: {data['title']}")
print(f"Body: {data['body']}")

# PART 3 — GET request with headers
print("\n--- PART 3: Request with Headers ---")

headers = {
    "Content-Type": "application/json",  # sending JSON
    "Accept": "application/json"          # want JSON back
}

response = requests.get(
    "https://jsonplaceholder.typicode.com/posts/2",
    headers=headers
)

print(f"Status Code: {response.status_code}")
print(f"Title: {response.json()['title']}")

# PART 4 — POST request
print("\n--- PART 4: POST Request ---")

new_post = {
    "title": "My Resume Analyzer Project",
    "body": "Built with Python and Groq API",
    "userId": 1
}

response = requests.post(
    "https://jsonplaceholder.typicode.com/posts",
    json=new_post
)

print(f"Status Code: {response.status_code}")  # 201 = Created
print(f"Created post ID: {response.json()['id']}")
print(f"Title: {response.json()['title']}")

# PART 5 — Error handling
print("\n--- PART 5: Error Handling ---")

response = requests.get("https://jsonplaceholder.typicode.com/posts/99999")

if response.status_code == 200:
    print("Success!")
elif response.status_code == 404:
    print("404 — Not found!")
elif response.status_code == 401:
    print("401 — Unauthorized! Check API key.")
elif response.status_code == 429:
    print("429 — Too many requests! Wait and retry.")
else:
    print(f"Error: {response.status_code}")

# PART 6 — How Groq API uses all of this
print("\n--- PART 6: Groq API under the hood ---")
print("""
POST → https://api.groq.com/v1/chat/completions
Headers → Authorization: Bearer your-key
Body → model + messages
Response → choices[0].message.content
""")