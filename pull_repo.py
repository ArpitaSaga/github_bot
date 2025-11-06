# pull_repo.py
import sys
import requests
import json

def create_pull_request(owner, repo, head, base, title, body, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json"
    }
    payload = {
        "title": title,
        "body": body,
        "head": head,
        "base": base
    }

    print(f"Creating pull request from {head} to {owner}/{repo}:{base} ...")

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        data = response.json()
        print("Pull request created successfully!")
        print("Pull Request URL:", data["html_url"])
    elif response.status_code == 422:
        print("Pull request already exists or branch names are invalid.")
    else:
        print("Failed to create pull request.")
        print("Status code:", response.status_code)
        print("Response:", response.text)


if __name__ == "__main__":
    if len(sys.argv) < 8:
        print("Usage: python pull_repo.py <owner> <repo> <head> <base> <title> <body> <token>")
        sys.exit(1)

    owner = sys.argv[1]
    repo = sys.argv[2]
    head = sys.argv[3]
    base = sys.argv[4]
    title = sys.argv[5]
    body = sys.argv[6]
    token = sys.argv[7]

    create_pull_request(owner, repo, head, base, title, body, token)
