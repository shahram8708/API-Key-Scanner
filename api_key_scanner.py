import requests
import re

GITHUB_TOKEN = "GITHUB_TOKEN"
GITHUB_USERNAME = "GITHUB_USERNAME" 

patterns = [
    r'AKIA[0-9A-Z]{16}', 
    r'AIza[0-9A-Za-z-_]{35}', 
    r'sk_live_[0-9a-zA-Z]{24}', 
    r'(?:\b|_)([0-9a-fA-F]{32})(?:\b|_)',
    r'(?:\b|_)([0-9a-fA-F]{40})(?:\b|_)',
]

GITHUB_API_URL = "https://api.github.com"

code_extensions = [".py", ".js", ".html", ".css", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp"]

ignored_directories = ["venv", "myenv", "node_modules", "__pycache__", "site-packages", "dist", "build"]

def fetch_repositories():
    repositories = []
    page = 1

    while True:
        url = f"{GITHUB_API_URL}/users/{GITHUB_USERNAME}/repos?page={page}&per_page=100"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            repos = response.json()
            if not repos: 
                break
            repositories.extend(repos)
            page += 1
        else:
            print(f"Error fetching repositories: {response.status_code} - {response.text}")
            break

    return repositories

def fetch_file_content(repo_name, file_path):
    url = f"{GITHUB_API_URL}/repos/{GITHUB_USERNAME}/{repo_name}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        file_data = response.json()
        if file_data["type"] == "file":
            return requests.get(file_data["download_url"]).text
    return None

def scan_content(content, file_path):
    matches = []
    for pattern in patterns:
        for match in re.finditer(pattern, content):
            matches.append((file_path, match.group(), match.start()))
    return matches

def scan_repo(repo_name):
    url = f"{GITHUB_API_URL}/repos/{GITHUB_USERNAME}/{repo_name}/git/trees/main?recursive=1"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        repo_tree = response.json()
        findings = []
        for item in repo_tree.get("tree", []):
            if item["type"] == "blob": 
                file_path = item["path"]
                if any(ignored_dir in file_path for ignored_dir in ignored_directories):
                    continue
                if any(file_path.endswith(ext) for ext in code_extensions):
                    print(f"Scanning file: {file_path}")
                    content = fetch_file_content(repo_name, file_path)
                    if content:
                        findings.extend(scan_content(content, file_path))
        return findings
    else:
        print(f"Error fetching repository tree for {repo_name}: {response.status_code} - {response.text}")
        return []

if __name__ == "__main__":
    print("Fetching repositories...")
    repos = fetch_repositories()

    if not repos:
        print("No repositories found or unable to fetch repositories.")
    else:
        findings = {}
        for repo in repos:
            repo_name = repo["name"]
            print(f"\nScanning repository: {repo_name}")
            repo_findings = scan_repo(repo_name)
            if repo_findings:
                findings[repo_name] = repo_findings

        if findings:
            print("\nPotential API keys found:")
            for repo_name, repo_findings in findings.items():
                print(f"\nRepository: {repo_name}")
                for file_path, key, position in repo_findings:
                    print(f"  File: {file_path} | Key: {key} | Position: {position}")
        else:
            print("No API keys found in any repository.")
