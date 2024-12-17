import openai
import typing as tp
from .utils import Util
import logging
from jinja2 import Environment,FileSystemLoader
import os
from pydantic import BaseModel

class InlineComment(BaseModel) :
    line : int
    comment : str

class Response(BaseModel) :
    inline_comments : tp.List[InlineComment]

class AIAnalyzer:
    def __init__(self, api_key : str, settings : tp.Dict):
        print(api_key[:5])
        self.client = openai.OpenAI(api_key=api_key)
        self.temperature = settings.get("temperature", 0.7)
        self.max_tokens = settings.get("max_tokens", 1000)
        self.code_styles = settings.get("code_style", {})
        self.model = settings.get("ai_model", "gpt-4o-mini")
        self.prompt_folder = "prompts"

        ## Setup for prompt templates (Might be updated to several prompts)
        templates_path = os.path.join(os.path.dirname(__file__), self.prompt_folder)
        self.env = Environment(loader=FileSystemLoader(templates_path))

    def make_prompt(self,diff : str,code : str, code_style : str) -> str:
        
        template = self.env.get_template("prompt_template.jinja2")
        numerated_code = Util.numerate_lines(code)
        prompt = template.render(diff=diff, code=numerated_code, code_style=code_style)
        return prompt

    def analyze_diff(self, diff : str , code : str, code_style : str) :
        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.make_prompt(diff,code,code_style)
                    },
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format=Response
            )
            content : Response | None  = response.choices[0].message.parsed
            print("Ответ от LLM:",content)
            return Util.parse_respone_test(content)

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
    


