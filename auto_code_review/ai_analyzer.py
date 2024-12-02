import openai
import typing as tp
from .utils import Util
import logging

class AIAnalyzer:
    def __init__(self, api_key : str, settings : tp.Dict):
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

    def analyze_diff(self, diff : str , code : str) -> tp.List[tp.Dict] :
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
            content : tp.List[str]  = []
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content.append(chunk.choices[0].delta.content)
            string_content : str  = " ".join(content)
            return Util.parse_response(string_content)

        except openai.APIError:
            logging.warning("Authentification Error: Check your API key.") ## logging
        except openai.RateLimitError:
            logging.warning("Rate limit exceeded: Try later.") ## logging
        except openai.APIConnectionError:
            logging.warning("Error while connecting to API: Check your internet connection.") ## logging
        except openai.BadRequestError as e:
            logging.warning(f"Invalid request to API: {e}") ## logging
        except Exception as e:
            logging.warning(f"An unknown error occured: {e}") ## logging
        return []
    


