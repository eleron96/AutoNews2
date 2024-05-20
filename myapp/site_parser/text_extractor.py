# myapp/site_parser/text_extractor.py
import requests
from bs4 import BeautifulSoup
from newspaper import Article

def extract_main_text(page_url):
    print(f"Извлечение текста со страницы: {page_url}")
    try:
        # Загружаем страницу и создаем объект BeautifulSoup
        response = requests.get(page_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Удаляем элементы, которые не являются частью основного контента
        for unwanted in soup(['header', 'footer', 'nav', 'aside', 'form', 'script', 'style']):
            unwanted.decompose()

        # Извлечение заголовка
        title = soup.title.string if soup.title else "Заголовок не указан"

        # Определение потенциальных контейнеров для основного контента
        content_selectors = [
            {'name': 'div', 'class_': 'post-body entry-content'},
            {'name': 'div', 'class_': 'blog-post-content'},
            {'name': 'div', 'class_': 'post-content'},
            {'name': 'div', 'class_': 'entry-content'},
            {'name': 'div', 'class_': 'elementor-widget-container'},
            {'name': 'article'},
            {'name': 'main'}
        ]

        # Функция для извлечения текста из всех подходящих элементов
        def extract_text_from_elements(elements):
            texts = []
            for element in elements:
                paragraphs = element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'figure'])
                texts.append('\n\n'.join(paragraph.get_text(strip=True) for paragraph in paragraphs))
            return texts

        # Извлечение основного текста по селекторам
        all_texts = []
        for selector in content_selectors:
            main_contents = soup.find_all(selector['name'], class_=selector.get('class_'))
            if main_contents:
                all_texts.extend(extract_text_from_elements(main_contents))

        # Конкатенируем все найденные тексты
        text = '\n\n'.join(all_texts)

        # Если основной текст не найден, используем newspaper как запасной вариант
        if not text:
            article = Article(page_url)
            article.download()
            article.parse()
            text = article.text

        # Извлечение автора из HTML
        author_selectors = [
            {'name': 'meta', 'attr_name': 'name', 'attr_value': 'author'},
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
            if 'attr_name' in selector:
                author_tag = soup.find(selector['name'], attrs={selector['attr_name']: selector['attr_value']})
            else:
                author_tag = soup.find(selector['name'], class_=selector.get('class_'))
            if author_tag:
                author = author_tag.get_text(strip=True) if 'attr_name' not in selector else author_tag['content']
                break


        return title, author or "Автор не указан", text
    except Exception as e:
        return "Ошибка при парсинге страницы", "Неизвестный автор", str(e)