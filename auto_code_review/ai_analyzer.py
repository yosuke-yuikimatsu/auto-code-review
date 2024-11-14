import openai
import json
import sys

class AIAnalyzer:
    def __init__(self, api_key, settings):
        self.client = openai.OpenAI(api_key=api_key)
        self.temperature = settings.get("temperature", 0.7)
        self.max_tokens = settings.get("max_tokens", 1000)
        self.code_styles = settings.get("code_style", {})
        self.model = settings.get("ai_model", "gpt-4o-mini")

    def analyze_diff(self, diff, file_extension):
        code_style = self.code_styles.get(file_extension,"")
        prompt = (
            "You are a code reviewer. For each code change provided below, "
            "generate a brief comment for each line in the diff. \n"
            "For lines that start with '+', analyze the added code and suggest improvements or highlight any potential issues, "
            f"including code-style changes according to {code_style} (if no code style is given, use the standard style for the language).\n"
            "For lines that start with '-', these lines have been removed from the code. Analyze the removed code and provide feedback on "
            "whether the removal might introduce any potential problems or bugs in the program.\n"
            "Return your response in JSON format, where each key is a line from the diff, and the value is your comment for that line.\n"
            "If no comment is needed for a line, skip it and do not include it in the JSON response.\n\n"
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

            json_response = response.choices[0].message.content
            analysis = json.loads(json_response)

            return self.parse_response(analysis,diff)

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

        return comments


