import openai
import json
import sys
import re

class AIAnalyzer:
    def __init__(self, api_key, settings):
        self.client = openai.OpenAI(api_key=api_key)
        self.temperature = settings.get("temperature", 0.7)
        self.max_tokens = settings.get("max_tokens", 1000)
        self.code_styles = settings.get("code_style", {})
        self.model = settings.get("ai_model", "gpt-4o-mini")

    def get_code_style(self,file_extension) :
        return self.code_styles.get(file_extension, "")

    def analyze_diff(self, diff, file_extension):
        code_style = self.get_code_style(file_extension)
        prompt = (
            "You are a code reviewer. For each code change provided below, "
            "generate a brief comment for each line in the diff. \n"
            "For lines that start with '+', analyze the added code and suggest improvements or highlight any potential issues, "
            f"including code-style changes according to {code_style} (if no code style is given, use the standard style for the language).\n"
            "For lines that start with '-', these lines have been removed from the code. Analyze the removed code and provide feedback on "
            "whether the removal might introduce any potential problems or bugs in the program.\n"
            f"Return your response as a Python string in a format - {"SOC(line (the whole itself without any changes) <<<>>> comment )FOC"} - where each pair is placed on its own line\n"
            "There must be no whitespace between line of code and <<<>>>"
            "If no comment is needed for a line, skip it and do not include it in the response\n\n"
            f"Code changes:\n{diff}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful code reviewer whose job is to review code diffs and provide feedback."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            response = response.choices[0].message.content
            print(response)
            response = self.response_to_dict(response)

            return self.parse_response(response,diff)

        except openai.APIError:
            print("Authentification Error: Check your API key.")
        except openai.RateLimitError:
            print("Rate limit exceeded: Try later.")
        except openai.APIConnectionError:
            print("Error while connecting to API: Check your internet connection.")
        except openai.BadRequestError as e:
            print(f"Invalid request to API: {e}")
        except Exception as e:
            print(f"An unknown error occured: {e}")
        sys.exit(1)
    
    @staticmethod
    def response_to_dict(response) :
        matches = re.findall(r"SOC(.*?)FOC", response, re.DOTALL)
        dict = {}

        for match in matches:
            line, comment = match.split("<<<>>>")
            if line.startswith('(') :
                line = line[1:]
            if comment.endswith(')') :
                comment = comment[:-1]
            dict[line] = comment
        return dict

    
    @staticmethod
    def parse_response(analysis,diff) :
        comments = []
        old_file_line_counter = 0
        new_file_line_counter = 0
        for line in diff.splitlines() :
            if line.startswith('-') :
                if line in analysis:
                    comments.append({
                        "deleted" : True,
                        "line_number" : old_file_line_counter,
                        "comment" : analysis[line]
                    })
                old_file_line_counter += 1
            elif line.startswith('+') :
                if line in analysis:
                    comments.append({
                        "deleted": False,
                        "line_number": new_file_line_counter,
                        "comment": analysis[line]
                    })
                new_file_line_counter += 1
            else:
                if line in analysis:
                    comments.append({
                        "deleted" : False,
                        "line_number": new_file_line_counter,
                        "comment" : analysis[line]
                    })
                old_file_line_counter += 1
                new_file_line_counter += 1
        print(comments)
        return comments


