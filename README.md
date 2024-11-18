### Step 1: Project Folder Structure

```
api-key-scanner/
├── api_key_scanner.py  
├── README.md 
├── requirements.txt   
```

### Step 2: The Python Script (`api_key_scanner.py`)

This will be the main script for your project. You can copy and paste your existing code into this file:

```python
import requests
import re

# GitHub Personal Access Token for authentication
GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"  # Replace with your GitHub token
GITHUB_USERNAME = "YOUR_GITHUB_USERNAME"  # Replace with your GitHub username

# Regular expressions for detecting API keys from any platform
patterns = [
    r'AKIA[0-9A-Z]{16}',  # AWS Access Key ID
    r'AIza[0-9A-Za-z-_]{35}',  # Google API Key
    r'sk_live_[0-9a-zA-Z]{24}',  # Stripe Live Secret Key
    r'(?:\b|_)([0-9a-fA-F]{32})(?:\b|_)',  # Generic 32-character hexadecimal
    r'(?:\b|_)([0-9a-fA-F]{40})(?:\b|_)',  # Generic 40-character hexadecimal
]

# GitHub API base URL
GITHUB_API_URL = "https://api.github.com"

# Extensions for programming language files
code_extensions = [".py", ".js", ".html", ".css", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp"]

# Directories to ignore
ignored_directories = ["venv", "myenv", "node_modules", "__pycache__", "site-packages", "dist", "build"]

# Function to fetch repositories using GitHub API
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

# Function to fetch repository file contents
def fetch_file_content(repo_name, file_path):
    url = f"{GITHUB_API_URL}/repos/{GITHUB_USERNAME}/{repo_name}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        file_data = response.json()
        if file_data["type"] == "file":
            return requests.get(file_data["download_url"]).text
    return None

# Function to scan file content for API keys
def scan_content(content, file_path):
    matches = []
    for pattern in patterns:
        for match in re.finditer(pattern, content):
            matches.append((file_path, match.group(), match.start()))
    return matches

# Function to scan repository for files and API keys
def scan_repo(repo_name):
    url = f"{GITHUB_API_URL}/repos/{GITHUB_USERNAME}/{repo_name}/git/trees/main?recursive=1"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        repo_tree = response.json()
        findings = []
        for item in repo_tree.get("tree", []):
            if item["type"] == "blob":  # Blob represents a file
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

# Main script execution
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
```

### Step 3: The `README.md` File

Create a `README.md` file to provide documentation for users of your repository. Here's an example README content:

```markdown
# API Key Scanner

## Overview
This project is a simple Python script that scans all public GitHub repositories of a user for potential API keys. The script looks for common API key patterns such as AWS Access Keys, Google API Keys, Stripe Keys, and other generic API key formats.

## Features
- Scans all public repositories of a GitHub user.
- Detects API keys from various platforms like AWS, Google Cloud, and Stripe.
- Allows easy modification to include new API key patterns.
- Prints results directly to the console.

## Requirements
- Python 3.6 or higher
- `requests` library

## Installation

### Clone the repository
```bash
git clone https://github.com/shahram8708/API-Key-Scanner.git
cd api-key-scanner
```

### Install dependencies
You can install the required dependencies using `pip`:
```bash
pip install -r requirements.txt
```

## Configuration
Before running the script, you need to configure the following:

1. Replace `YOUR_GITHUB_TOKEN` and `YOUR_GITHUB_USERNAME` in the `api_key_scanner.py` script with your own GitHub credentials.

2. Optionally, you can modify the API key patterns list to include other platforms.

## Usage
Once everything is configured, simply run the following command to start scanning:

```bash
python api_key_scanner.py
```

The script will scan all your public GitHub repositories for API keys and print the results to the console.

### Example Output:
```
Fetching repositories...
Scanning repository: my-repo
Scanning file: my_file.py
Potential API keys found:
Repository: my-repo
  File: my_file.py | Key: AKIAEXAMPLEKEY1234 | Position: 50
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```

### Step 4: The `requirements.txt` File

To specify the dependencies for your project, create a `requirements.txt` file:

```
requests==2.28.1
```

This will ensure that when other people clone your repository, they can install the necessary dependencies using `pip install -r requirements.txt`.

### Step 5: Push to GitHub

1. Create a new repository on GitHub (e.g., `api-key-scanner`).
2. Follow the instructions on GitHub to push your local code to the new repository:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/shahram8708/API-Key-Scanner.git
git push -u origin main
```

### Conclusion

Once you push your project to GitHub with the provided files, others will be able to clone it, configure it with their GitHub credentials, and start scanning repositories for potential API keys.
