import argparse
from .core import Reviewer

def main():
    parser = argparse.ArgumentParser(description="Automatic code review for GitHub PRs")
    parser.add_argument("--config", help="Path to configuration file", default="config.yaml")
    args = parser.parse_args()

    reviewer = Reviewer(config_file=args.config)
    reviewer.review_pull_request()

if __name__ == "__main__":
    main()
