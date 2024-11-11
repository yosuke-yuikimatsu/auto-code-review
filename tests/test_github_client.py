import unittest
from unittest.mock import patch
import requests
from auto_code_review.github_client import GitHubClient

class TestGitHubClient(unittest.TestCase):
    def setUp(self):
        self.token = "fake_token"
        self.client = GitHubClient(self.token)
        self.owner = "test_owner"
        self.repo = "test_repo"
        self.pr_number = 1
        self.filename = "test_file.py"

    @patch("requests.get")
    def test_get_pr_files_with_diffs(self, mock_get):
        # Mock Github API answer
        mock_response = [
            {
                "filename": "test_file.py",
                "patch": "@@ -1,3 +1,3 @@\n- old line\n+ new line\n"
            },
            {
                "filename": "another_file.py",
                "patch": "@@ -2,2 +2,2 @@\n- another old line\n+ another new line\n"
            }
        ]
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        # Testing methods
        diffs = self.client.get_pr_files_with_diffs(self.owner, self.repo, self.pr_number)
        self.assertEqual(len(diffs), 2)
        self.assertEqual(diffs[0]["filename"], "test_file.py")
        self.assertEqual(diffs[0]["patch"], "@@ -1,3 +1,3 @@\n- old line\n+ new line\n")
        self.assertEqual(diffs[1]["filename"], "another_file.py")
        self.assertEqual(diffs[1]["patch"], "@@ -2,2 +2,2 @@\n- another old line\n+ another new line\n")

    @patch("requests.get")
    def test_get_commit_id_for_file(self, mock_get):
        mock_commits_response = [
            {"sha": "commit_sha_1"},
            {"sha": "commit_sha_2"},
        ]
        
        mock_commit_details_response = {
            "files": [
                {"filename": "test_file.py"}
            ]
        }

        mock_get.side_effect = [
            
            unittest.mock.Mock(status_code=200, json=lambda: mock_commits_response),
            
            unittest.mock.Mock(status_code=200, json=lambda: mock_commit_details_response),
        ]

        
        commit_id = self.client.get_commit_id_for_file(self.owner, self.repo, self.pr_number, self.filename)
        self.assertEqual(commit_id, "commit_sha_2")

    @patch("requests.post")
    def test_post_inline_comment(self, mock_post):
        
        mock_post.return_value.status_code = 201

        
        try:
            self.client.post_inline_comment(
                self.owner,
                self.repo,
                self.pr_number,
                "commit_sha_2",
                "test_file.py",
                1,
                "Test comment"
            )
        except Exception as e:
            self.fail(f"post_inline_comment вызвал ошибку: {e}")

        
        mock_post.assert_called_once()

if __name__ == "__main__":
    unittest.main()
