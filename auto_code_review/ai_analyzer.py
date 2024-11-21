import openai
import typing as tp
from .utils import Util

class AIAnalyzer:
    def __init__(self, api_key, settings):
        self.client = openai.OpenAI(api_key=api_key)
        self.temperature = settings.get("temperature", 0.7)
        self.max_tokens = settings.get("max_tokens", 1000)
        self.code_styles = settings.get("code_style", {})
        self.model = settings.get("ai_model", "gpt-4o-mini")

    def make_prompt(self,diff : str,code : str) -> str:
        prompt = f"""Could you describe briefly {{problems}} for the next code with the given git diffs or make suggestions for realization and code-style?

### Instructions on Line Numbering:
1. The provided code contains line numbers as comments in the format `## <number>` at the beginning of each line (including empty lines).
2. Use the line numbers from these comments when referring to any line in the code.
3. Do not comment on or analyze the line numbers themselves (e.g., `##1`, `##2`). These are technical markers for orientation and should not be included in your analysis.
4. Treat all lines, including empty or whitespace-only lines, as regular lines for numbering and analysis.
5. In your response, refer to the lines strictly by their absolute number as given in the comments.

### Response Format:
For each issue, return in the following format:
`line_number : your comment`

If there are no issues, respond with `{{no_response}}`.

### Example:
#### Input Code:
```python
  ##1
  ##2
print("Hello")  ##3
  ## 4
def foo():  ##5
    pass  ##6
```
#### Output:
3 : consider replacing Hello with Hello,World!

git diffs:
{diff}

code:
{Util.numerate_lines(code)}"""

        return prompt

    def analyze_diff(self, diff , code)  :
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
            return Util.parse_response(content)

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
    


