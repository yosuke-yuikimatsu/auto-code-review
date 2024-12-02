
# Automatic Code Review

This repository uses GitHub Actions for automatic code review on every Pull Request. The code review process is powered by the **auto-code-review** library, which connects to the OpenAI API to generate inline comments and suggestions for code improvements.

## GitHub Actions Configuration

Below is the configuration for the GitHub Actions workflow:

```yaml
name: Auto Code Review

on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches:
      - '*'

jobs:
  pr_review:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write

    steps:
      - name: Check out repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.12"

      - name: Install auto-code-review from PyPi
        run: |
          python -m pip install --upgrade pip
          pip install auto-code-review

      - name: Run auto code review
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GITHUB_HEAD_REF: ${{ github.head_ref }}
          GITHUB_BASE_REF: ${{ github.base_ref }}
          REPO_OWNER: ${{ github.repository_owner }}
          REPO_NAME: ${{ github.event.repository.name }}
          PULL_NUMBER: ${{ github.event.number }}
        run: auto-code-review --config config.yaml
```

## How It Works

1. **Trigger on `pull_request`:** The workflow is triggered when a Pull Request is created, updated, or reopened.
2. **Set Up Python Environment:** The workflow sets up Python version `3.12` and installs the `auto-code-review` package from PyPI.
3. **Run Auto Code Review:** The `auto-code-review` command is executed to analyze the changes in the Pull Request using OpenAI’s API. The tool will leave inline comments on the code changes with  potential issues.

## Prerequisites

Before using this workflow, you need to add the following secrets to your repository settings:

- **`GITHUB_TOKEN`**: A GitHub token automatically provided in your repository (no extra setup needed).
- **`OPENAI_API_KEY`**: Your OpenAI API key, which must be added manually in `Settings` -> `Secrets and variables` -> `Actions` -> `New repository secret`.

## Example Usage

To enable automatic code review, simply create a Pull Request from any branch in your repository which contains the needed worklflow file. GitHub Actions will automatically trigger the analysis, and inline comments will be added directly to the Pull Request with feedback on code style, potential optimizations, and any detected issues.

## Additional Notes

- This workflow supports any branch (`branches: ['*']`), meaning it will run for Pull Requests involving any target branch.
- The tool is configured via a `config.yaml` file, which should be present in the root directory of your repository. This file allows you to specify various settings such as the AI model, temperature and file extensions

## Sample Config File (`config.yaml`)

```yaml
# config.yml

analysis:
  file_extensions: [".py", ".cpp",".yaml"]

ai_settings:
  ai_model: gpt-4o-mini
  temperature: 0.7
  max_tokens: 1000
```

In this configuration:
- **`ai_model`** sets the chatgpt model which will be used to create comments(gpt-4o-mini by default)
- **`file_extensions`** sets the extensions of files which will be auto-reviewed(Necessary to write extensions)
- **`temperature`** controls the randomness of the suggestions - higher values make responses more creative(0.7 by default).
- **`max_tokens`** limits the number of tokens generated by the AI.(1000 by default)

## Troubleshooting

If the workflow fails with a `422 Unprocessable Entity` error, it could be due to:
- An incorrect `position` value for inline comments.
- An invalid or outdated `commit_id`.
- Missing or incorrect `path` for the file being commented on.

Ensure that your configuration and API keys are set up correctly, and check the logs in GitHub Actions for more details.
