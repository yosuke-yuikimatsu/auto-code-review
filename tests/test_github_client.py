import unittest
from unittest.mock import patch, Mock
from auto_code_review.github_client import GitHubClient
import subprocess
import requests

"""It may be reasonable to actually use real git commands in GitHub Actions
and then comapre these results to the results of API.
 However at the given moment it looks excessive.
 So, that's why mocked tests are currently used"""

class TestGitHubClient(unittest.TestCase):

    def setUp(self):
        self.client = GitHubClient(
            token="test_token",
            repo="test_repo",
            owner="test_owner",
            pr_number=123,
            base_ref="main",
            head_ref="feature-branch"
        )

    @patch("subprocess.run")
    def test_get_remote_name(self, mock_run):
        mock_run.return_value = Mock(returncode=0, stdout="origin\tgit@github.com:test_owner/test_repo.git (fetch)\n")
        result = self.client.get_remote_name()
        self.assertEqual(result, "origin")
        mock_run.assert_called_with(["git", "remote", "-v"], stdout=subprocess.PIPE, text=True)

    @patch("subprocess.run")
    def test_get_last_commit_sha(self, mock_run):
        mock_run.return_value = Mock(returncode=0, stdout='"abcdef1234567890"\n')
        result = self.client.get_last_commit_sha("test_file.py")
        self.assertEqual(result, "abcdef1234567890")
        mock_run.assert_called_with(["git", "log", "-1", "--format=\"%H\"", "--", "test_file.py"], stdout=subprocess.PIPE, text=True)

    @patch("subprocess.run")
    def test_get_diff_files(self, mock_run):
        mock_run.return_value = Mock(returncode=0, stdout="file1.py\nfile2.cpp\n")
        result = self.client.get_diff_files("origin")
        self.assertEqual(result, ["file1.py", "file2.cpp"])
        mock_run.assert_called_with(
            ["git", "diff", "--name-only", "origin/main", "origin/feature-branch"],
            stdout=subprocess.PIPE, text=True
        )

    @patch("subprocess.run")
    def test_get_diff_in_file(self, mock_run):
        mock_run.return_value = Mock(returncode=0, stdout="diff --git a/file1.py b/file1.py\n+print('Hello')")
        result = self.client.get_diff_in_file("origin", "file1.py")
        self.assertIn("print('Hello')", result)
        mock_run.assert_called_with(
            ["git", "diff", "origin/main", "origin/feature-branch", "--", "file1.py"],
            stdout=subprocess.PIPE, text=True
        )

    @patch("requests.post")
    def test_post_comment_to_line(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        self.client.post_comment_to_line("Test comment", "abcdef1234567890", "test_file.py", 42)

        mock_post.assert_called_with(
            "https://api.github.com/repos/test_owner/test_repo/pulls/123/comments",
            json={
                "body": "Test comment",
                "commit_id": "abcdef1234567890",
                "path": "test_file.py",
                "line": 42,
                "side": "RIGHT"
            },
            headers=self.client.headers
        )

    @patch("requests.post")
    def test_post_comment_general(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        self.client.post_comment_general("General comment")

        mock_post.assert_called_with(
            "https://api.github.com/repos/test_owner/test_repo/issues/123/comments",
            json={"body": "General comment"},
            headers=self.client.headers
        )

    @patch("subprocess.run")
    def test_subprocess_error(self, mock_run):
        mock_run.return_value = Mock(returncode=1, stderr="Some error occurred")

        with self.assertRaises(Exception) as context:
            self.client.get_remote_name()
        
        self.assertIn("Error running", str(context.exception))

if __name__ == "__main__":
    unittest.main()
