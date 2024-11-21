import typing as tp

def parse_diffs(diff : str) -> tp.List[tuple[int,int]]:
        ##print("diff:",diff)
        intervals : tp.List[tuple[int,int]] = []
        for line in diff.splitlines():
            if line.startswith("@@"):
                try:
                    start,context = line[line.find('+') + 1 : -2].split(',')
                    context = context.split("@@")[0]
                    end = int(start) + int(context) - 1
                    intervals.append((int(start),end))
                except:
                    continue
        
        return intervals

diff = """ diff --git a/auto_code_review/core.py b/auto_code_review/core.py
index 9a29346..31f49cf 100644
--- a/auto_code_review/core.py
+++ b/auto_code_review/core.py
@@ -2,43 +2,34 @@ import yaml
 import os
 from .github_client import GitHubClient
 from .ai_analyzer import AIAnalyzer
+from .utils import Util
 
 class Reviewer:
     def __init__(self, config_file="config.yml"): #  Get configuration file with settings for auto code-review
         self.config = self.load_config(config_file)
 
-        # Get tokens which are stored in secrets of repository - OpenAI API key and GitHub token
-        github_token = os.getenv("GITHUB_TOKEN")
-        openai_api_key = os.getenv("OPENAI_API_KEY")
-
-        # Get head_ref and body_ref for getting diffs
-        head_ref = os.getenv("GITHUB_HEAD_REF")
-        base_ref = os.getenv("GITHUB_BASE_REF")
-
-        owner = os.getenv("REPO_OWNER")
-        repo = os.getenv("REPO_NAME")
-        pr_number = os.getenv("PULL_NUMBER")
-
-
-        if not github_token:
-            raise ValueError("GITHUB_TOKEN is not found. Make sure to write it in your workflow file and access it via GitHub secrets")
-        if not openai_api_key:
-            raise ValueError("OPENAI_API_KEY is not found. Make sure to write it in your worflow file and access it via GitHub secrets")
-        if not head_ref:
-            raise ValueError("GITHUB_HEAD_REF is not found. Make sure to write it in your workflow file via github.")
-        if not base_ref:
-            raise ValueError("GITHUB_BASE_REF is not found. Make sure to write it in you workflow file via github.")
-        if not owner:
-            raise ValueError("REPO_OWNER is not found. Make sure to define it in your workflow file.")
-        if not repo:
-            raise ValueError("REPO_NAME is not found. Make sure to define it in your workflow file.")
-        if not pr_number:
-            raise ValueError("PULL_NUMBER is not found. Make sure to define it in your workflow file.")
-
+        required_env_vars = {
+            "GITHUB_TOKEN": "Make sure to write it in your workflow file and access it via GitHub secrets.",
+            "OPENAI_API_KEY": "Make sure to write it in your workflow file and access it via GitHub secrets.",
+            "GITHUB_HEAD_REF": "Make sure to write it in your workflow file via github.",
+            "GITHUB_BASE_REF": "Make sure to write it in your workflow file via github.",
+            "REPO_OWNER": "Make sure to define it in your workflow file.",
+            "REPO_NAME": "Make sure to define it in your workflow file.",
+            "PULL_NUMBER": "Make sure to define it in your workflow file."
+        }
+
+        # Check needed environment variables
+        env_vars = {}
+        for var, error_message in required_env_vars.items():
+            value = os.getenv(var)
+            if not value:
+                raise ValueError(f"{var} is not found. {error_message}")
+            env_vars[var] = value
 
         # Initialzie instances of GitHub interactor and OpenAI analyzer
-        self.github = GitHubClient(github_token,repo,owner,pr_number,base_ref,head_ref)
-        self.analyzer = AIAnalyzer(openai_api_key, self.config.get("ai_settings"))
+        self.github = GitHubClient(env_vars["GITHUB_TOKEN"],env_vars["REPO_NAME"],env_vars["REPO_OWNER"],
+                                   env_vars["PULL_NUMBER"],env_vars["GITHUB_BASE_REF"],env_vars["GITHUB_HEAD_REF"])
+        self.analyzer = AIAnalyzer(env_vars["OPENAI_API_KEY"], self.config.get("ai_settings"))
 
 
     def load_config(self, config_file):
@@ -95,15 +86,19 @@ class Reviewer:
             if len(file_diffs) == 0:
                 print(f"{file} diffs are empty")
                 continue
-
+            
+            intervals = Util.parse_diffs(file_diffs)
+            
             responses = self.analyzer.analyze_diff(file_diffs,file_content)
 
+
             for response in responses:
                 line = response.get("line")
                 comment = response.get("comment")
-                print("file:",file)
-                print("line:",line)
-                print("comment:",comment)
+                print("\n")
+                if not Util.check_availability_to_post_comment(line,intervals) :
+                    print("Line is out of available context")
+                    continue
                 if not comment:
                     print("No comments were given")
                     continue"""

print(parse_diffs(diff))