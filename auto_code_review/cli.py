import argparse
from .core import Reviewer

def main():
    parser = argparse.ArgumentParser(description="Automatic code review for GitHub PRs")
    parser.add_argument("--config", help="Path to configuration file", default="config.yml")
    parser.add_argument("--owner", required=True, help="Repository owner")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--pr", type=int, required=True, help="Pull request number")
    args = parser.parse_args()

    reviewer = Reviewer(config_file=args.config)
    reviewer.review_pull_request(owner=args.owner, repo=args.repo, pr_number=args.pr)

if __name__ == "__main__":
    main()
