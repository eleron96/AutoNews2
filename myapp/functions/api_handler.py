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
            "content": f"Summarize the following news text in a blog format "
                       f"written by {author}. Please use the author's name in the text. "
                       f"Rewrite the text in your own words as a freeform paraphrase. "
                       f"Make the story engaging and seamless. Limit the character count to 800!:\n{text}"
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
