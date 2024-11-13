import requests

class GitHubClient:
    def __init__(self, token):
        self.token = token # Intialize GitHub API
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        
    @staticmethod
    def parse_patch(patch) :
        parsed_patch = ""
        for line in patch.splitlines(True) :
            if not (line.startswith("-")) :
                parsed_patch += line
        return parsed_patch
    
    def get_pr_files_with_diffs(self, owner, repo, pr_number):
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        files = response.json()
        diffs = []
        for file in files:
            filename = file["filename"]
            patch = file.get("patch", "")
            if patch:
                diffs.append({"filename": filename, "patch": patch})
        return diffs

    def post_inline_comment(self, owner, repo, pr_number, commit_id, path, position, comment):
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        data = {
            "body": comment,
            "commit_id": commit_id,
            "path": path,
            "position": position
        }
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
        except:
            raise ValueError("Request failed to post comment")
    
    def get_commit_id_for_file(self, owner, repo, pr_number, filename):
        """
        Find SHA of a commit in which the given file was changed from PR 
        """
        # Get all commits from PR
        commits_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/commits"
        commits_response = requests.get(commits_url, headers=self.headers)
        commits_response.raise_for_status()
        commits = commits_response.json()

        # Iterate over all PR's commits to find the one in which the given file was changed most recently
        for commit in reversed(commits):
            commit_sha = commit["sha"]

            commit_details_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}"
            details_response = requests.get(commit_details_url, headers=self.headers)
            details_response.raise_for_status()
            commit_files = details_response.json().get("files", [])

            for file in commit_files:
                if file["filename"] == filename:
                    return commit_sha

        raise ValueError(f"Commit for file {filename} was not found in PR #{pr_number}.")