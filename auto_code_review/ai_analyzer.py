import openai

class AIAnalyzer:
    def __init__(self, api_key, settings):
        openai.api_key = api_key
        self.temperature = settings.get("temperature", 0.7)
        self.max_tokens = settings.get("max_tokens", 1000)
        self.model = settings.get("ai_model", "gpt-4o-mini")

    def analyze_diff(self, diff):
        prompt = (
            "You are a code reviewer. For each code change provided below, "
            "generate a brief, one-line comment including the line number from the diff. "
            "Format your response as 'Line {line_number}: {comment}'. "
            "If no comment is needed, skip that line.\n\n"
            f"Code changes:\n{diff}"
        )

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful code reviewer."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        analysis = response['choices'][0]['message']['content'].split("\n")
        comments = []

        # Parse response and then store it as tuple (line_number, comment)
        for line in analysis:
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
