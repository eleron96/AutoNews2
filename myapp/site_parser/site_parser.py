# myapp/site_parser/site_parser.py
import requests
from bs4 import BeautifulSoup


def parse_site(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Форматируем результаты парсинга в виде HTML
        parsed_data = f"""
        <h3>Title: {soup.title.string if soup.title else 'Без заголовка'}</h3>
        <p>{soup.get_text()}</p>
        """
        return parsed_data
    except requests.RequestException as e:
        return f'<p>Error: {str(e)}</p>'
