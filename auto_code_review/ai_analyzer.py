import openai
import typing as tp
from .utils import Util
import logging
from jinja2 import Environment,FileSystemLoader
import os

class AIAnalyzer:
    def __init__(self, api_key : str, settings : tp.Dict):
        self.client = openai.OpenAI(api_key=api_key)
        self.temperature = settings.get("temperature", 0.7)
        self.max_tokens = settings.get("max_tokens", 1000)
        self.code_styles = settings.get("code_style", {})
        self.model = settings.get("ai_model", "gpt-4o-mini")
        self.prompt_folder = "prompts"

        templates_path = os.path.join(os.path.dirname(__file__), self.prompt_folder)

        print(templates_path)

        # Настроим Jinja2 для загрузки шаблонов из папки
        self.env = Environment(loader=FileSystemLoader(templates_path))

    def make_prompt(self,diff : str,code : str, code_style : str) -> str:
        
        template = self.env.get_template("prompt_template.jinja2")
        numerated_code = Util.numerate_lines(code)
        prompt = template.render(diff=diff, code=numerated_code, code_style=code_style)
        print("prompt:",prompt)
        return prompt

    def analyze_diff(self, diff : str , code : str, code_style : str) -> tp.List[tp.Dict] :
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.make_prompt(diff,code,code_style)
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
            print("Ответ от LLM:",string_content)
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
    


