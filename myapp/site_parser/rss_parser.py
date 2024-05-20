import feedparser
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .date_utils import parse_date, display_date

def find_rss_url(page_url):
    try:
        response = requests.get(page_url)
        response.raise_for_status()  # Проверка на успешный запрос
        soup = BeautifulSoup(response.content, 'html.parser')
        rss_links = soup.find_all('link', type='application/rss+xml')

        if rss_links:
            return urljoin(page_url, rss_links[0]['href'])
        else:
            print("Не удалось найти RSS ссылку на странице.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе страницы: {e}")
        return None

def get_rss_feed(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка на успешный запрос
        feed = feedparser.parse(response.content)
        return feed
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе RSS фида: {e}")
        return None

def display_feed(feed, start_date, end_date):
    if not feed:
        print("Не удалось получить RSS фид.")
        return

    print(f"\n\nНовости из RSS фида: {feed.feed.get('title', 'Без названия')}")
    print("-" * 40)

    for entry in feed.entries:
        try:
            published_date = parse_date(entry.published)
            if start_date <= published_date <= end_date:
                print(f"Заголовок: {entry.title}")
                print(f"Ссылка: {entry.link}")
                print(f"Дата публикации: {display_date(entry.published)}")
                print("-" * 40)
        except Exception as e:
            print(f"Ошибка при обработке даты публикации: {e}")

def process_rss_feed(page_url, start_date, end_date):
    rss_url = find_rss_url(page_url)
    if rss_url:
        feed = get_rss_feed(rss_url)
        display_feed(feed, start_date, end_date)
