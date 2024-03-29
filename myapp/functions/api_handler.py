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

def summarize_text(text, author):
    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": f"As a reviewer, I'm examining various blogs and authors. Today, I'm focusing on a piece written by {author}. "
                       f"I will provide my own interpretation and summary of the original text, ensuring to maintain the essence while transforming the style. "
                       f"My goal is to present an engaging and seamless narrative that reflects the core themes and messages of the original work, "
                       f"all while keeping within an 800-character limit. Here's the text:\n{text}"

        }],
        temperature=0.5,
        max_tokens=1024)
        # Возвращаем к исходной структуре ответа
        message = response.choices[0].message.content
        return clean_text(message)
    except Exception as e:
        return str(e)

# Пример использования функции в вашем приложении
def create_or_update_news(title, content, author):
    summary = summarize_text(content, author)  # Получаем резюме новости
    news, created = News.objects.update_or_create(
        title=title,
        defaults={'content': content, 'author': author, 'summary': summary},
    )
    return news
