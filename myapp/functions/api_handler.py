from openai import OpenAI
import re
from django.conf import settings

from ..models import News

# Получение API ключа из настроек Django
api_key = settings.API_KEY

client = OpenAI(api_key=api_key)

def clean_text(text):
    # Ваша функция очистки текста
    return re.sub(r'\n\s*\n', '\n', text.strip())

def summarize_text(text, author, model_choice, char_count=800):
    try:
        # print('Модель для summarize_text:', model_choice)  # Отладочное сообщение
        # print("Первая функция", text)
        response = client.chat.completions.create(
            model=model_choice,  # Используем выбранную модель
            messages=[{
                "role": "user",
                "content": f"As a reviewer, I'm examining various blogs and authors. Today, I'm focusing on a piece written by {author}. Please note that the text was not written by me, I am only retelling it, so it should not be in the first person, the text was written by the {author} "
                           f"I will provide my own interpretation and summary of the original text, ensuring to maintain the essence while transforming the style. "
                           f"My goal is to present an engaging and seamless narrative that reflects the core themes and messages of the original work, "
                           f"all while keeping within a {char_count}-character limit. use only simple text formatting, indentations, and punctuation. Here's the text:\n{text}"
            }],
            temperature=0.5,
            max_tokens=1024
        )
        message = response.choices[0].message.content
        return clean_text(message)
    except Exception as e:
        return str(e)


def summarize_text_brief(text, author, model_choice, char_count=800):
    try:
        response = client.chat.completions.create(
            model=model_choice,  # Используем выбранную модель
            messages=[{
                "role": "user",
                "content": f"Summarize the following text written by {author} in the third person, ensuring it remains within {char_count} characters. Remove any unnecessary formatting. Here's the text:\n{text}"
                           f"There is no need to retell the text verbatim. We need to engage the reader by highlighting what is interesting for them in this blog. Avoid using promotional language and enthusiasm."
            }],
            temperature=0.5,
            max_tokens=1024
        )
        message = response.choices[0].message.content
        return clean_text(message)
    except Exception as e:
        return str(e)

# Пример вызова функции
text = "Your text here"
author = "Author Name"
model_choice = "chosen-model"
result = summarize_text_brief(text, author, model_choice, char_count=800)
print(result)


def get_article_author(url, model_choice):
    try:
        response = client.chat.completions.create(
            model=model_choice,  # Используем выбранную модель
            messages=[{
                "role": "user",
                "content": f"Who is the author of the article at this URL: {url}?"
                           f"Answer without context. If the author is unknown, write the name of the company that owns the blog. Provide only the answer!"
            }],
            temperature=0.5,
            max_tokens=1024
        )
        message = response.choices[0].message.content
        return message.strip()
    except Exception as e:
        return str(e)