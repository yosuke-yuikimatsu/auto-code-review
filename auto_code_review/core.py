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

        # Get head_ref and body_ref for getting diffs
        head_ref = os.getenv("GITHUB_HEAD_REF")
        base_ref = os.getenv("GITHUB_BASE_REF")

        owner = os.getenv("REPO_OWNER")
        repo = os.getenv("REPO_NAME")
        pr_number = os.getenv("PULL_NUMBER")


        if not github_token:
            raise ValueError("GITHUB_TOKEN is not found. Make sure to write it in your workflow file and access it via GitHub secrets")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY is not found. Make sure to write it in your worflow file and access it via GitHub secrets")
        if not head_ref:
            raise ValueError("GITHUB_HEAD_REF is not found. Make sure to write it in your workflow file via github.")
        if not base_ref:
            raise ValueError("GITHUB_BASE_REF is not found. Make sure to write it in you workflow file via github.")
        if not owner:
            raise ValueError("REPO_OWNER is not found. Make sure to define it in your workflow file.")
        if not repo:
            raise ValueError("REPO_NAME is not found. Make sure to define it in your workflow file.")
        if not pr_number:
            raise ValueError("PULL_NUMBER is not found. Make sure to define it in your workflow file.")


        # Initialzie instances of GitHub interactor and OpenAI analyzer
        self.github = GitHubClient(github_token,repo,owner,pr_number,base_ref,head_ref)
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

    def review_pull_request(self) :
        remote_name = self.github.get_remote_name()

        changed_files = self.github.get_diff_files(remote_name)

        extensions = self.config.get("analysis",{}).get("file_extensions",[])
        
        if not extensions:
            raise ValueError("No file_extensions found.File_extensions must be written in config.yaml file")

        for file in changed_files:

            _, file_extension = os.path.splitext(file)

            if file_extension not in extensions:
                print("Unsupported extensions")
                continue
            
            try:
                with open(file, 'r') as file_opened:
                    file_content = file_opened.read()
            except FileNotFoundError:
                print(f"{file} was removed")
                continue

            if len(file_content) == 0:
                print(f"{file} is empty")
                continue

            file_diffs = self.github.get_diff_in_file(remote_name,file)

            if len(file_diffs) == 0:
                print(f"{file} diffs are empty")

            responses = self.analyzer.analyze_diff(file_diffs,file_content)

            for response in responses:
                line = response.get("line")
                comment = response.get("comment")
                print("file:",file)
                print("line:",line)
                print("comment:",comment)
                if not comment or line == 0:
                    print("No comments were given")
                    continue
                if line is None:
                    self.github.post_comment_general(comment)
                else:
                    self.github.post_comment_to_line(comment,self.github.get_last_commit_sha(file),file,line)

                


