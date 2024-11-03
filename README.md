#### 1. Project Description and Features

This project is designed for the automated analysis of code based on events occurring in GitHub or GitLab. Its core functionality includes:

- **Code Analysis:** Upon each push or merge request (PR), the project automatically initiates a code review using the OpenAI API or a selected LLM.

- **Feedback:** The analysis results are provided as comments on the PR

- **Customizability:** Users can configure the types of checks (such as style, potential bugs, optimization) via a configuration file named `.codereview.yaml`.

#### 2. User Interface Interaction Scenario

1. **Setup:** The user configures a GitHub/GitLab webhook for push or PR events and adds the OpenAI API key to the repository settings file.

2. **Execution:** The script is automatically triggered to analyze the code after each push or PR creation.

3. **Results:** Error reports or recommendations are displayed directly in the PR

#### 3. Project Structure

- **API Layer** — A module for interacting with the OpenAI API or the chosen LLM.

- **GitHub/GitLab Webhook Handler** — A module for processing incoming requests from the version control platform.

- **Analyzer** — The core logic for code analysis, including checks and extensibility options (e.g., PEP8 support or optimization recommendations).

- **Report Generator** — A module responsible for creating the analysis report.

- **Configuration Handler** — A module for reading and processing the `.codereview.yaml` configuration file.



#### 4. Roles

- Responsible for the whole project - Dmitry Geyvandov
- Contact @BigTittyWomenLover if needed