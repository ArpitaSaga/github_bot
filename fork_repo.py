import sys
import requests

def fork_repo(owner, repo, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/forks"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    print(f"Forking {owner}/{repo} to your account...")

    response = requests.post(url, headers=headers)
    if response.status_code in (200, 202):
        data = response.json()
        print("Fork created successfully!")
        print("Fork URL:", data["html_url"])
    elif response.status_code == 422:
        print("You already have a fork of this repository.")
    else:
        print("Failed to fork repository.")
        print("Status code:", response.status_code)
        print("Response:", response.text)

if __name__ == "__main__":
    owner = sys.argv[1]
    repo = sys.argv[2]
    token = sys.argv[3]
    fork_repo(owner, repo, token)
