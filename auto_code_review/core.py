import yaml
import os
from .github_client import GitHubClient
from .ai_analyzer import AIAnalyzer
from .utils import Util

class Reviewer:
    def __init__(self, config_file="config.yml"): #  Get configuration file with settings for auto code-review
        self.config = self.load_config(config_file)

        required_env_vars = {
            "GITHUB_TOKEN": "Make sure to write it in your workflow file and access it via GitHub secrets.",
            "OPENAI_API_KEY": "Make sure to write it in your workflow file and access it via GitHub secrets.",
            "GITHUB_HEAD_REF": "Make sure to write it in your workflow file via github.",
            "GITHUB_BASE_REF": "Make sure to write it in your workflow file via github.",
            "REPO_OWNER": "Make sure to define it in your workflow file.",
            "REPO_NAME": "Make sure to define it in your workflow file.",
            "PULL_NUMBER": "Make sure to define it in your workflow file."
        }

        # Check needed environment variables
        env_vars = {}
        for var, error_message in required_env_vars.items():
            value = os.getenv(var)
            if not value:
                raise ValueError(f"{var} is not found. {error_message}")
            env_vars[var] = value

        # Initialzie instances of GitHub interactor and OpenAI analyzer
        self.github = GitHubClient(env_vars["GITHUB_TOKEN"],env_vars["REPO_NAME"],env_vars["REPO_OWNER"],
                                   env_vars["PULL_NUMBER"],env_vars["GITHUB_BASE_REF"],env_vars["GITHUB_HEAD_REF"])
        self.analyzer = AIAnalyzer(env_vars["OPENAI_API_KEY"], self.config.get("ai_settings"))


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
            print("file from diff:",file)

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
                continue

            responses = self.analyzer.analyze_diff(file_diffs,file_content)

            intervals = Util.parse_diffs(file_diffs)


            for response in responses:
                line = response.get("line")
                comment = response.get("comment")
                if not Util.check_availability_to_post_comment(line,intervals) :
                    print("Line is out of available context")
                    continue
                if not comment:
                    print("No comments were given")
                    continue
                if line is None or line == 0:
                    self.github.post_comment_general(comment)
                else:
                    self.github.post_comment_to_line(comment,self.github.get_last_commit_sha(file),file,line)

                


