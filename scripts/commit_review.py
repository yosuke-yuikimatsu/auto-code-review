import os
import openai
import sys
import argparse

# Разбор аргументов командной строки
parser = argparse.ArgumentParser()
parser.add_argument("--file", help="Name of the file being reviewed")
args = parser.parse_args()

# Проверка наличия API ключа OpenAI
if not os.environ.get("OPENAI_API_KEY"):
    print("No OpenAI API key found")
    sys.exit(1)

# Установка API ключа
openai.api_key = os.environ["OPENAI_API_KEY"]

# Получение параметров из переменных окружения
model_engine = os.environ["MODEL"]
commit_message = os.environ["COMMIT_MESSAGE"]  # Используем COMMIT_MESSAGE вместо COMMIT_TITLE
max_length = int(os.environ["MAX_LENGTH"])
prompt_base = os.environ["PROMPT"]

# Разделение заголовка и тела коммита
commit_lines = commit_message.split("\n", 1)
commit_title = commit_lines[0]
commit_body = commit_lines[1] if len(commit_lines) > 1 else ""

# Чтение содержимого файла, переданного через stdin
code = sys.stdin.read()
file_name = args.file or "Unknown file"
header = f"Commit title: '{commit_title}'\nCommit message: '{commit_body}'\nFile: {file_name}\n"

# Формирование запроса для OpenAI
prompt = f"{prompt_base}\n\n{header}\nCode:\n```\n{code}\n
"

# Обрезка, если запрос превышает допустимую длину
if len(prompt) > max_length:
    print(f"Prompt too long for OpenAI: {len(prompt)} characters, truncating to {max_length} characters.")
    prompt = prompt[:max_length]

# Параметры для OpenAI API
kwargs = {
    'model': model_engine,
    'messages': [
        {"role": "system", "content": "You are a helpful assistant and code reviewer."},
        {"role": "user", "content": prompt},
    ],
    'temperature': 0.5,
    'max_tokens': 1024
}

# Отправка запроса и получение ответа
try:
    response = openai.ChatCompletion.create(**kwargs)
    review_text = response.choices[0].message.content.strip() if response.choices else "No valid response from OpenAI."
except Exception as e:
    review_text = f"OpenAI failed to generate a review: {e}"

# Вывод результата
print(f"Review for {file_name}:\n{review_text}")