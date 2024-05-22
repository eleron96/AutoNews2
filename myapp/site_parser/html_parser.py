import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .date_utils import display_date
from datetime import datetime

def find_blog_posts(page_url):
    try:
        response = requests.get(page_url)
        response.raise_for_status()  # Проверка на успешный запрос
        soup = BeautifulSoup(response.content, 'html.parser')

        # Находим все карточки с блогами для speckle.systems/blog
        speckle_blog_posts = soup.find_all('div', class_='flex flex-col rounded-lg transition shadow hover:shadow-2xl overflow-hidden')

        # Находим все карточки с блогами для testfit.io/blog
        testfit_blog_posts = soup.find_all('div', class_='resources_item')

        # Находим все карточки с блогами для parametric.se/blog
        parametric_blog_posts = soup.find_all('div', class_='blog-post-item w-dyn-item')

        blogs = []

        # Обработка блогов speckle.systems/blog
        for post in speckle_blog_posts:
            title_tag = post.find('p', class_='text-xl font-semibold text-gray-900 dark:text-gray-200')
            title = title_tag.get_text(strip=True) if title_tag else 'Без заголовка'

            description_tag = post.find('p', class_='mt-3 text-base text-gray-500 line-clamp-3 md:line-clamp-4')
            description = description_tag.get_text(strip=True) if description_tag else 'Без описания'

            link_tag = post.find('a', href=True)
            link = urljoin(page_url, link_tag['href']) if link_tag else 'Без ссылки'

            date_tag = post.find('time')
            date = date_tag.get_text(strip=True) if date_tag else 'Без даты'

            blogs.append({
                'title': title,
                'description': description,
                'link': link,
                'date': date
            })

        # Обработка блогов testfit.io/blog
        for post in testfit_blog_posts:
            title_tag = post.find('div', class_='heading-style-h4')
            title = title_tag.get_text(strip=True) if title_tag else 'Без заголовка'

            description_tag = post.find('div', class_='text-style-subheader')
            description = description_tag.get_text(strip=True) if description_tag else 'Без описания'

            link_tag = post.find('a', href=True)
            link = urljoin(page_url, link_tag['href']) if link_tag else 'Без ссылки'

            date_tag = post.find('time')
            date = date_tag.get_text(strip=True) if date_tag else 'Без даты'

            blogs.append({
                'title': title,
                'description': description,
                'link': link,
                'date': date
            })

        # Обработка блогов parametric.se/blog
        for post in parametric_blog_posts:
            title_tag = post.find('h3', class_='tile-heading aligned')
            title = title_tag.get_text(strip=True) if title_tag else 'Без заголовка'

            description_tag = post.find('p', class_='small-text')
            description = description_tag.get_text(strip=True) if description_tag else 'Без описания'

            link_tag = post.find('a', class_='blog-pillar-link w-inline-block', href=True)
            link = urljoin(page_url, link_tag['href']) if link_tag else 'Без ссылки'

            date_tag = post.find('time')
            date = date_tag.get_text(strip=True) if date_tag else 'Без даты'

            blogs.append({
                'title': title,
                'description': description,
                'link': link,
                'date': date
            })

        return blogs
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе страницы: {e}")
        return []

def display_blog_posts(blog_posts, start_date, end_date):
    if not blog_posts:
        print("Не удалось найти блоги.")
        return

    print("\n\nНовости с HTML страницы:")
    print("-" * 40)
    for blog in blog_posts:
        try:
            # Используем текущую дату, если дата не указана
            published_date = datetime.strptime(blog['date'], '%d %b %Y').date() if blog['date'] != 'Без даты' else datetime.today().date()
            if start_date <= published_date <= end_date:
                print(f"Заголовок: {blog['title']}")
                print(f"Краткое описание: {blog['description']}")
                print(f"Ссылка: {blog['link']}")
                print(f"Время публикации: {display_date(blog['date'])}")
                print("-" * 40)
        except Exception as e:
            print(f"Ошибка при обработке даты публикации: {e}")

def process_html_page(page_url, start_date, end_date):
    blog_posts = find_blog_posts(page_url)
    display_blog_posts(blog_posts, start_date, end_date)
