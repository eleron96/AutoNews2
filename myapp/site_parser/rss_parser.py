import feedparser
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)

def find_rss_url(page_url):
    try:
        response = requests.get(page_url)
        response.raise_for_status()  # Проверка на успешный запрос
        soup = BeautifulSoup(response.content, 'html.parser')
        rss_links = soup.find_all('link', type='application/rss+xml')

        if rss_links:
            return urljoin(page_url, rss_links[0]['href'])
        else:
            logger.error("Не удалось найти RSS ссылку на странице.")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе страницы: {e}")
        return None

def get_rss_feed(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка на успешный запрос
        feed = feedparser.parse(response.content)
        return feed
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе RSS фида: {e}")
        return None

def process_rss_feed(page_url):
    rss_url = find_rss_url(page_url)
    if rss_url:
        feed = get_rss_feed(rss_url)
        if feed:
            urls = [entry.link for entry in feed.entries[:2]]  # Получаем только последние два URL
            logger.info(f"Последние два URL: {urls}")
            return urls
    return []
