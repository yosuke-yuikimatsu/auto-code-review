import requests
import subprocess
import typing as tp
import logging

class GitHubClient:
    '''Github Client is a class which executes all interactions 
    with GitHub via either Git Commands or REST API'''
    def __init__(self, token,repo,owner,pr_number,base_ref,head_ref):
        self.token = token # Intialize GitHub API
        self.headers = { # Needed for getting access to posting comments
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.repo = repo
        self.owner = owner
        self.pr_number = pr_number
        self.base_ref = base_ref
        self.head_ref = head_ref
        self.__url_add_comment = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        self.__url_add_issue = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    
    ## Since using interacting via GitHub API is much more time-consuming git command are used directly instead
    ## It is worth saying that they can be used only in GitHub Actions because of copying the whole repository

    @staticmethod
    def __run_subprocess(options : tp.List[str]):
        '''Key function of interaction with GitHub via Git Commands
        It is a base for running various commands on GitHub VM
        In options the command itself is stored as a list of strings'''

        result = subprocess.run(options, stdout=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            raise Exception(f"Error running {options}: {result.stderr}")
    
    def get_remote_name(self) :
        command = ["git", "remote", "-v"]
        result = self.__run_subprocess(command)
        lines = result.strip().splitlines()
        return lines[0].split()[0]
    
    def get_last_commit_sha(self,file) -> str:
        command = ["git", "log", "-1", "--format=\"%H\"", "--", file]
        result = self.__run_subprocess(command)
        lines = result.strip().splitlines()
        return lines[0].split()[0].replace('"', "")
    
    def get_diff_files(self,remote_name) :
        command = ["git", "diff", "--name-only", f"{remote_name}/{self.base_ref}", f"{remote_name}/{self.head_ref}"]
        result = self.__run_subprocess(command)
        return result.strip().splitlines()
    
    def get_diff_in_file(self,remote_name,file_path) -> str:
        command = ["git", "diff", f"{remote_name}/{self.base_ref}", f"{remote_name}/{self.head_ref}", "--", file_path]
        return self.__run_subprocess(command)

    def post_comment_to_line(self, text, commit_id, file_path, line):
        '''For purposes of economy LLM only analyzes the new version of code
        with diffs. So, inline comments are posted to the right side(new ver of file) only.
        Might be fixed in the near future'''

        body = {
            "body": text,
            "commit_id": commit_id,
            "path" : file_path,
            "line" : line,
            "side" : "RIGHT"
        }
        try:
            response = requests.post(self.__url_add_comment, json = body, headers = self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.warning(f"failed to post comment on the line: {line} in {file_path} : {e}") ## logging

    def post_comment_general(self, text):
        body = {
            "body": text
        }
        response = requests.post(self.__url_add_issue, json = body, headers = self.headers)
        response.raise_for_status()
    





    