# myapp/site_parser/text_extractor.py
import requests
from bs4 import BeautifulSoup
from newspaper import Article


def extract_main_text(page_url):
    try:
        response = requests.get(page_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Определение потенциальных контейнеров для основного контента
        content_selectors = [
            {'name': 'div', 'class_': 'post-body entry-content'},
            {'name': 'div', 'class_': 'blog-post-content'},
            {'name': 'div', 'class_': 'post-content'},
            {'name': 'div', 'class_': 'entry-content'},
            {'name': 'article'},
            {'name': 'main'}
        ]

        # Поиск автора статьи
        author_selectors = [
            {'name': 'span', 'class_': 'author-name'},
            {'name': 'div', 'class_': 'author'},
            {'name': 'p', 'class_': 'author'},
            {'name': 'div', 'class_': 'post-header_author-wrapper'},
            {'name': 'span', 'class_': 'byline-author'},
            {'name': 'a', 'class_': 'author-name'},
            {'name': 'a', 'class_': 'byline-author'}
        ]

        author = None
        for selector in author_selectors:
            author_tag = soup.find(selector['name'],
                                   class_=selector.get('class_'))
            if author_tag:
                author = author_tag.get_text(strip=True)
                break

        # Попытка найти основной контент по каждому из селекторов
        for selector in content_selectors:
            main_content = soup.find(selector['name'],
                                     class_=selector.get('class_'))
            if main_content:
                paragraphs = main_content.find_all(
                    ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote',
                     'figure'])
                text = '\n\n'.join(
                    paragraph.get_text(strip=True) for paragraph in paragraphs)
                if text:
                    title = soup.title.string if soup.title else "Заголовок не указан"
                    return title, author or "Автор не указан", text

        # Если основной текст не найден, используем newspaper
        article = Article(page_url)
        article.download()
        article.parse()

        text = article.text
        author = ', '.join(
            article.authors) if article.authors else author or "Автор не указан"
        title = article.title if article.title else "Заголовок не указан"

        return title, author, text
    except Exception as e:
        return "Ошибка при парсинге страницы", "Неизвестный автор", str(e)
