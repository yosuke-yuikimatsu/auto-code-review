import unittest
from auto_code_review.github_client import GitHubClient

class TestGitHubClient(unittest.TestCase):
    def setUp(self):
        self.client = GitHubClient("fake_token")

    def test_parse_patch_with_additions_and_deletions(self):
        patch = """@@ -3,7 +3,7 @@
 context_line_1
-context_line_2
-old_line = 'This line was removed'
+new_line = 'This line was added'
 context_line_3
 unchanged_line
"""
        expected_output = """@@ -3,7 +3,7 @@
 context_line_1
+new_line = 'This line was added'
 context_line_3
 unchanged_line
"""
        result = self.client.parse_patch(patch)
        self.assertEqual(result, expected_output)

    def test_parse_patch_with_only_additions(self):
        patch = """@@ -1,3 +1,3 @@
+added_line_1
 context_line_1
+added_line_2
"""
        expected_output = """@@ -1,3 +1,3 @@
+added_line_1
 context_line_1
+added_line_2
"""
        result = self.client.parse_patch(patch)
        self.assertEqual(result, expected_output)

    def test_parse_patch_with_only_deletions(self):
        patch = """@@ -1,3 +0,0 @@
-deleted_line_1
-deleted_line_2
"""
        expected_output = """@@ -1,3 +0,0 @@
"""
        result = self.client.parse_patch(patch)
        self.assertEqual(result, expected_output)

    def test_parse_patch_with_no_changes(self):
        patch = """@@ -1,3 +1,3 @@
 unchanged_line_1
 unchanged_line_2
"""
        expected_output = """@@ -1,3 +1,3 @@
 unchanged_line_1
 unchanged_line_2
"""
        result = self.client.parse_patch(patch)
        self.assertEqual(result, expected_output)

    def test_parse_patch_empty_input(self):
        patch = ""
        expected_output = ""
        result = self.client.parse_patch(patch)
        self.assertEqual(result, expected_output)

if __name__ == "__main__":
    unittest.main()
