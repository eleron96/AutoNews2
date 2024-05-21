import feedparser
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_rss_feed(url):
    try:
        logger.info(f"Запрос RSS фида по URL: {url}")
        response = requests.get(url)
        response.raise_for_status()  # Проверка на успешный запрос
        feed = feedparser.parse(response.content)
        if feed.bozo == 0:  # Проверяем, что фид корректно распарсился
            logger.info("RSS фид успешно получен и распаршен")
            return feed
        else:
            logger.error("Некорректный RSS фид.")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе RSS фида: {e}")
        return None

def find_rss_url(page_url):
    try:
        logger.info(f"Запрос страницы по URL: {page_url}")
        response = requests.get(page_url)
        response.raise_for_status()  # Проверка на успешный запрос
        soup = BeautifulSoup(response.content, 'html.parser')
        rss_links = soup.find_all('link', type='application/rss+xml')

        if rss_links:
            rss_url = urljoin(page_url, rss_links[0]['href'])
            logger.info(f"Найдена RSS ссылка: {rss_url}")
            return rss_url
        else:
            # Проверка на конкретные случаи, например Blogspot
            if "blogspot.com" in page_url:
                rss_url = f"{page_url.rstrip('/')}/feeds/posts/default?alt=rss"
                logger.info(f"Сформирована RSS ссылка для Blogspot: {rss_url}")
                return rss_url
            logger.error("Не удалось найти RSS ссылку на странице.")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе страницы: {e}")
        return None

def process_rss_feed(page_url):
    # Сначала пробуем обработать URL как RSS фид
    logger.info(f"Начинаем обработку URL: {page_url} как RSS фида")
    feed = get_rss_feed(page_url)
    if feed:
        urls = [entry.link for entry in feed.entries[:2]]  # Получаем только последние два URL
        logger.info(f"Последние два URL из RSS фида: {urls}")
        return urls

    # Если URL не является RSS фидом, пытаемся найти RSS ссылку на странице
    logger.info(f"URL не является RSS фидом, пытаемся найти RSS ссылку на странице: {page_url}")
    rss_url = find_rss_url(page_url)
    if rss_url:
        feed = get_rss_feed(rss_url)
        if feed:
            urls = [entry.link for entry in feed.entries[:2]]  # Получаем только последние два URL
            logger.info(f"Последние два URL из найденного RSS фида: {urls}")
            return urls

    logger.info("RSS ссылки не найдены, возвращаем пустой список")
    return []
