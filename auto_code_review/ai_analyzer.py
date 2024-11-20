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
        prompt = f"""
            Could you describe briefly {{problems}} for the next code with given git diffs or make suggestions to realization and code-style?
            Please, also, do not add intro words, just print errors in the format: "line_number : cause effect".
            If there are no {{problems}}, just say "{{no_response}}".

            DIFFS:

            {diff}

            Full code from the file:

            {code}
            """.strip()

        return prompt

    def analyze_diff(self, diff, code):
        print("DIFF:",diff)
        print("CODE:",code)
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
        sys.exit(1)
    

    @staticmethod
    def parse_response(input) :
        if input is None or not input:
            return []
        
        lines = input.strip().split("\n")
        models = []

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

            models.append({"line" : number, "comment" : full_text})
        return models
    


