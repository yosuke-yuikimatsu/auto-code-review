import openai
import sys

class AIAnalyzer:
    def __init__(self, api_key, settings):
        self.client = openai.OpenAI(api_key=api_key)
        self.temperature = settings.get("temperature", 0.7)
        self.max_tokens = settings.get("max_tokens", 1000)
        self.code_styles = settings.get("code_style", [])
        self.model = settings.get("ai_model", "gpt-4o-mini")

    def get_code_style(self,file_extension) :
        return self.code_styles.get(file_extension, "")

    def analyze_diff(self, diff, file_extension):
        code_style = self.get_code_style(file_extension)
        prompt = (
            "You are a code reviewer. For each code change provided below, "
            "generate a brief, one-line comment including the line number from the diff. "
            " You do not need to explain what code does. Your main goal is to suggest some improvements"
            f"in realization if needed or code-style changes according to {code_style}(if no code style given choose the basic one for given language) and highlight possible errors if they may occur."
            "So if everything is ok with a code line there is no need to anyhow comment it."
            "Format your response as 'Line {line_number}: {comment}'. "
            "Do not write comments to deleted lines(lines that start with -)"
            "If there is nothing to comment at all just reply with several whitespaces"
            "If no comment is needed, skip that line.\n\n"
            f"Code changes:\n{diff}"
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful code reviewer whose job is to review diffs in some PR."
                     "Keep in mind that you must act like a real human developer."
                      "So, you do not need to explain what function does - you must only suggest some changes in logic, highlight possible errors"
                      "and maybe suggest some code-style improvements"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            analysis = response.choices[0].message.content.split("\n")

            return self.parse_response(analysis)
            
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
    def parse_response(analysis) :
        comments = []

        # Parse response and then store it as tuple (line_number, comment)
        for line in analysis:
            if not line:
                continue

            # Getting rid of enumeration
            if line[0].isdigit() and line[1] == ".":
                line = line.split(".", 1)[1].strip()
            
            if line.strip() and line.startswith("Line"):
                try:
                    # Extract line number and comment for it
                    line_number_str, comment = line.split(":", 1)
                    line_number = int(line_number_str.replace("Line", "").strip())
                    comments.append((line_number, comment.strip()))
                except ValueError:
                    # Ignore lines with wrong format
                    continue

        return comments
