import yaml
import os
from .github_client import GitHubClient
from .ai_analyzer import AIAnalyzer

class Reviewer:
    def __init__(self, config_file="config.yml"): #  Get configuration file with settings for auto code-review
        self.config = self.load_config(config_file)

        # Get tokens which are stored in secrets of repository - OpenAI API key and GitHub token
        github_token = os.getenv("GITHUB_TOKEN")
        openai_api_key = os.getenv("OPENAI_API_KEY")

        if not github_token:
            raise ValueError("GITHUB_TOKEN is not found. Make sure to write it in your workflow file and access it via GitHub secrets")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY is not found. Make sure to write it in your worflow file and access it via GitHub secrets")

        # Initialzie instances of GitHub interactor and OpenAI analyzer
        self.github = GitHubClient(github_token)
        self.analyzer = AIAnalyzer(openai_api_key, self.config.get("ai_settings"))

    def load_config(self, config_file):
    # Check whether configuration file exists
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file  '{config_file}' is not found.")

        try:
            with open(config_file, "r") as file:
                config = yaml.safe_load(file)

                # Check if configuration file is empty
                if config is None:
                    raise ValueError("Configuration file is either empty or wrong format")

                return config
        except yaml.YAMLError as e:
            raise ValueError(f"Error occured while parsing YAML file'{config_file}': {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to download configuration file '{config_file}': {e}")  

    def review_pull_request(self, owner, repo, pr_number):
        extensions = self.config.get("analysis", {}).get("file_extensions")  # Files which must be reviewed

        if not extensions:
            raise KeyError(
                "'file_extensions' key in 'analysis' section of the configuration file is absent.\n"
                "It must be added to the configuration file in the following format: [\".ext\", \".ext\",...]"
                )


        files = self.github.get_pr_files_with_diffs(owner, repo, pr_number) # Get all files from PR which were changed
        for file in files:
            filename = file["filename"]
            patch = file["patch"]
            code = file["content"]

            # Filter changed files by extension
            for ext in extensions:
                if filename.endswith(ext):
                    extension = ext
                    break
            else:
                continue

            comments = self.analyzer.analyze_diff(patch,extension,code) # Generate code-review as a list of dicts for a changed file via ChatGPT prompt
            commit_id = self.github.get_commit_id_for_file(owner,repo,pr_number,filename)
            for comment in comments:
                body = comment.get("comment","")
                line = comment.get("line",-1)
                if (not body) or (line == -1) :
                    raise ValueError(f"Comments to patch: {patch} are incorrectly formated\n.body: {body}\nline: {line}\n")
                self.github.post_inline_comment(owner,repo,pr_number,commit_id,filename,line,body)