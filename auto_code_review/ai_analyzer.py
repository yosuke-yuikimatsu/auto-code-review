import openai
import sys

class AIAnalyzer:
    def __init__(self, api_key, settings):
        self.client = openai.OpenAI(api_key=api_key)
        self.temperature = settings.get("temperature", 0.7)
        self.max_tokens = settings.get("max_tokens", 1000)
        self.code_styles = settings.get("code_style", {})
        self.model = settings.get("ai_model", "gpt-4o-mini")

    @staticmethod
    def make_prompt(diff,code) :
        prompt = f"""Could you describe briefly {{problems}} for the next code with the given git diffs or make suggestions for realization and code-style?

### Instructions on Line Numbering:
1. Count all lines in the provided code, including empty lines, lines with only whitespace, and lines with only comments (e.g., "##").
2. Do not include the "git diffs" section in the line numbering of the code.
3. Assign line numbers sequentially, starting from 1 for the very first line in the file.
4. Treat empty lines, whitespace-only and comment-only lines as regular lines, ensuring they are included in the numbering.
5. In your response, refer to the lines by their absolute number in the file, as per the above rules.

### Response Format:
For each issue, return in the following format:
`line_number : your comment`

If there are no issues, respond with `{{no_response}}`.

### Example:
#### Input Code:
```python
##

print("Hello")


def foo():
    pass
    
### Example output:
3 : consider replacing Hello with Hello, World! 

git diffs :
{diff}

code:
{code}"""


        return prompt

    def analyze_diff(self, diff, code):
        print("PROMPT:",self.make_prompt(diff,code))
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.make_prompt(diff,code)
                    },
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )
            content = []
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content.append(chunk.choices[0].delta.content)
            content = " ".join(content)
            return self.parse_response(content)

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
    

    @staticmethod
    def parse_response(input) :
        if input is None or not input:
            return []
        
        lines = input.strip().split("\n")
        response = []

        for full_text in lines:
            number_str = ''
            number = 0
            full_text = full_text.strip()
            if len( full_text ) == 0:
                continue

            reading_number = True
            for char in full_text.strip():
                if reading_number:
                    if char.isdigit():
                        number_str += char
                    else:
                        break

            if number_str:
                number = int(number_str)

            response.append({"line" : number, "comment" : full_text})
        return response
    


