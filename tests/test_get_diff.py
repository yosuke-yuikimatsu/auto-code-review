import os
from auto_code_review.github_client import GitHubClient
import sys


token = os.getenv("GITHUB_TOKEN")
owner = os.getenv("GITHUB_REPOSITORY_OWNER", "yosuke-yuikimatsu")
repo = os.getenv("GITHUB_REPOSITORY_NAME", "auto-code-review")
pr_number = int(os.getenv("PR_NUMBER", 1))

github_client = GitHubClient(token)

diffs = github_client.get_pr_files_with_diffs(owner, repo, pr_number)

print("Changed files and their patches:")
for diff in diffs:
    filename = diff["filename"]
    patch = diff["patch"]
    print(f"\nFile: {filename}\npatch:\n{patch}\n")

sys.exit(0)
