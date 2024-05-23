import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages  # Импортируем messages из django.contrib
from django.views.decorators.csrf import csrf_protect
from myapp.site_parser.site_parser import parse_site
from myapp.site_parser.text_extractor import extract_main_text
import logging
import coloredlogs
from django.urls import reverse
from django.test import RequestFactory

from .functions.api_handler import summarize_text, summarize_text_brief, get_article_author
from .functions.forms import NewsForm, URLForm

# Create your views here.
from django.shortcuts import render

from .models import News, URL
from .site_parser.rss_parser import process_rss_feed
from .site_parser.html_parser import find_blog_posts
from django.http import JsonResponse

from functools import wraps
from time import time
import uuid

# Настройка цветного логирования с изменением формата даты и времени
coloredlogs.install(
    level='DEBUG',
    fmt='%(levelname)s %(asctime)s %(name)s[%(process)d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level_styles={
        'debug': {'color': 'green'},
        'info': {'color': 'blue'},
        'warning': {'color': 'yellow'},
        'error': {'color': 'red', 'bold': True},
        'critical': {'color': 'red', 'bold': True, 'background': 'white'}
    },
    field_styles={
        'asctime': {'color': 'cyan'},
        'hostname': {'color': 'magenta'},
        'levelname': {'bold': True},
        'name': {'color': 'blue'},
        'programname': {'color': 'cyan'},
        'process': {'color': 'yellow'}
    }
)

# Создание декоратора для логирования времени выполнения функций
def log_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        logger.info(f"Function {func.__name__} executed in {end_time - start_time:.4f} seconds")
        return result
    return wrapper

logger = logging.getLogger(__name__)



def home(request):
    return render(request, 'myapp/home.html')

def history_view(request):
    news_list = News.objects.all().order_by('-published_at')  # Сортировка по дате и времени
    return render(request, 'myapp/history.html', {'news_list': news_list})

def news_detail(request, pk):
    news = get_object_or_404(News, pk=pk)
    model_version = news.model_version if news.model_version else "Данные отсутствуют"
    char_count_requested = news.char_count_requested if news.char_count_requested else "Данные отсутствуют"
    char_count_received = news.char_count_received if news.char_count_received else "Данные отсутствуют"

    context = {
        'news': news,
        'model_version': model_version,
        'char_count_requested': char_count_requested,
        'char_count_received': char_count_received
    }

    return render(request, 'myapp/news_detail.html', context)

def dashboard_view(request):
    return render(request, 'myapp/settings.html')  # Указываем правильный путь к шаблону

def add_news_form(request):
    form = NewsForm()  # Пустая форма
    return render(request, 'myapp/add_news_form.html', {'form': form})

@csrf_protect
@require_POST
def update_settings(request):
    engine_select = request.POST.get('engine_select', 'gpt-3.5-turbo')
    char_count = int(request.POST.get('char_count', 800))

    # Сохраняем настройки в session
    request.session['engine_select'] = engine_select
    request.session['char_count'] = char_count

    messages.success(request, 'Настройки успешно обновлены')
    return redirect('settings')  # Имя должно совпадать с именем URL в urls.py

@require_POST
def add_news(request):
    form = NewsForm(request.POST)
    if form.is_valid():
        new_news = form.save(commit=False)
        engine_select = request.session.get('engine_select', 'gpt-3.5-turbo')
        char_count = request.session.get('char_count', 800)

        original_content = new_news.content
        summarized_content_temp = summarize_text(original_content, new_news.author,
                                            engine_select, char_count)
        summarized_content = summarize_text_brief(summarized_content_temp, new_news.author,
                                            engine_select, char_count)
        new_news.content = summarized_content
        new_news.model_version = engine_select
        new_news.char_count_requested = char_count
        new_news.char_count_received = len(summarized_content)
        new_news.save()
        messages.success(request, 'Новость успешно добавлена')
        return redirect('history')
    else:
        messages.error(request, 'Ошибка добавления новости')
        return redirect('home')

@require_POST  # Убедитесь, что этот вид может быть вызван только через POST-запрос
def delete_news(request, pk):
    news = get_object_or_404(News, pk=pk)
    news.delete()
    return redirect('history')  # Правильное название

def parsing_site(request):
    summarized_data = None
    summarized_brief_data = None
    message = None
    if request.method == "POST":
        url = request.POST.get("url")
        if url:
            logger.info(f"Получен URL для парсинга: {url}")
            # Проверка наличия URL в базе данных
            if News.objects.filter(link=url).exists():
                message = "Эта новость уже есть в базе данных."
                logger.info(f"Эта новость уже есть в базе данных: {url}")
            else:
                title, author, parsed_data = extract_main_text(url)
                logger.info(f"Полученны данные из URL: {url} | Заголовок: {title} | Автор: {author}")

                if parsed_data:
                    engine_select = request.session.get('engine_select', 'gpt-3.5-turbo')
                    logger.info(f"Selected engine: {engine_select}")

                    # Получение автора статьи, если он не был найден
                    if not author or author == 'Автор не указан':
                        url_object = URL.objects.filter(address=url).first()
                        if url_object and url_object.description:
                            author = url_object.description
                        else:
                            author = get_article_author(url, engine_select)
                        logger.info(f"Author determined: {author}")

                    char_count = request.session.get('char_count', 800)
                    logger.info(f"Character count for summary: {char_count}")

                    summarized_data = summarize_text(parsed_data, author, engine_select, char_count)
                    if summarized_data:
                        summarized_brief_data = summarize_text_brief(summarized_data, author, engine_select, char_count)
                        logger.info(f"Summarized data: {summarized_brief_data[:100]}...")

                        # Сохранение данных в модель News
                        news_entry = News(
                            author=author,
                            link=url,
                            title=title,
                            content=summarized_brief_data,
                            model_version=engine_select,
                            char_count_requested=char_count,
                            char_count_received=len(summarized_brief_data)
                        )
                        news_entry.save()
                        message = "Результат успешно сохранен в базе данных!"
                        logger.info(f"News entry saved for URL: {url}")
                else:
                    logger.warning(f"No data extracted from URL: {url}")

    return render(request, 'myapp/parsing.html', {
        'summarized_data': summarized_brief_data,
        'message': message
    })

def url_list(request):
    urls = URL.objects.all()
    return render(request, 'myapp/url_list.html', {'urls': urls})

def add_url(request):
    if request.method == 'POST':
        form = URLForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('url_list')
    else:
        form = URLForm()
    return render(request, 'myapp/add_url.html', {'form': form})

def edit_url(request, pk):
    url = get_object_or_404(URL, pk=pk)
    if request.method == 'POST':
        form = URLForm(request.POST, instance=url)
        if form.is_valid():
            form.save()
            return redirect('url_list')
    else:
        form = URLForm(instance=url)
    return render(request, 'myapp/edit_url.html', {'form': form})

def delete_url(request, pk):
    url = get_object_or_404(URL, pk=pk)
    if request.method == 'POST':
        url.delete()
        return redirect('url_list')
    return render(request, 'myapp/delete_url.html', {'url': url})

@csrf_protect
@require_POST
def update_frequency(request):
    frequency_select = request.POST.get('frequency_select', 'every_day')

    # Сохраняем настройки в session
    request.session['frequency_select'] = frequency_select

    messages.success(request, 'Частота проверки успешно обновлена')
    return redirect('dashboard')

@csrf_protect
@require_POST
def update_frequency(request):
    frequency_select = request.POST.get('frequency_select', 'every_day')
    request.session['frequency_select'] = frequency_select
    messages.success(request, 'Частота проверки успешно обновлена')
    return redirect('dashboard')

@log_execution_time
def check_now(request):
    request_id = uuid.uuid4()  # Уникальный идентификатор запроса
    urls = URL.objects.all()
    all_last_urls = []
    for url in urls:
        logger.info(f"[{request_id}] Начинаем обработку URL: {url.address}", extra={'request_id': request_id})
        try:
            last_urls = process_rss_feed(url.address)
            for last_url in last_urls:
                if last_url and last_url != 'undefined':
                    logger.info(f"[{request_id}] Отправляем URL в парсер: {last_url}", extra={'request_id': request_id})
                    try:
                        # Создаем POST-запрос к parsing_site
                        factory = RequestFactory()
                        post_request = factory.post(reverse('parsing_site'), data={'url': last_url})
                        post_request.session = request.session  # устанавливаем сессию
                        response = parsing_site(post_request)
                        logger.info(f"[{request_id}] Ответ от parsing_site для URL: {last_url} - статус: {response.status_code}", extra={'request_id': request_id})
                        if response.status_code == 200:
                            logger.info(f"[{request_id}] Новость сохранена для URL: {last_url}", extra={'request_id': request_id})
                        else:
                            logger.error(f"[{request_id}] Ошибка при вызове parsing_site: {response.status_code}", extra={'request_id': request_id})
                    except Exception as e:
                        logger.error(f"[{request_id}] Ошибка при вызове parsing_site: {e}", extra={'request_id': request_id})
            if last_urls:
                all_last_urls.extend([url for url in last_urls if url and url != 'undefined'])
        except Exception as e:
            logger.error(f"[{request_id}] Ошибка при проверке URL {url.address}: {e}", extra={'request_id': request_id})

        # Дополнительная проверка через HTML парсер, если новостей не найдено через RSS
        if not last_urls:
            try:
                logger.info(f"[{request_id}] Проверяем HTML страницу: {url.address}", extra={'request_id': request_id})
                blog_posts = find_blog_posts(url.address)
                if blog_posts:
                    # Возьмем два последних URL из найденных блогов
                    last_urls = [post['link'] for post in blog_posts[:2] if post['link']]
                    logger.info(f"[{request_id}] Последние два URL из HTML парсера: {last_urls}", extra={'request_id': request_id})
                    for last_url in last_urls:
                        if last_url and last_url != 'undefined':
                            logger.info(f"[{request_id}] Отправляем URL в парсер: {last_url}", extra={'request_id': request_id})
                            try:
                                # Создаем POST-запрос к parsing_site
                                factory = RequestFactory()
                                post_request = factory.post(reverse('parsing_site'), data={'url': last_url})
                                post_request.session = request.session  # устанавливаем сессию
                                response = parsing_site(post_request)
                                logger.info(f"[{request_id}] Ответ от parsing_site для URL: {last_url} - статус: {response.status_code}", extra={'request_id': request_id})
                                if response.status_code == 200:
                                    logger.info(f"[{request_id}] Новость сохранена для URL: {last_url}", extra={'request_id': request_id})
                                else:
                                    logger.error(f"[{request_id}] Ошибка при вызове parsing_site: {response.status_code}", extra={'request_id': request_id})
                            except Exception as e:
                                logger.error(f"[{request_id}] Ошибка при вызове parsing_site: {e}", extra={'request_id': request_id})
                    if last_urls:
                        all_last_urls.extend([url for url in last_urls if url and url != 'undefined'])
            except Exception as e:
                logger.error(f"[{request_id}] Ошибка при обработке HTML страницы: {e}", extra={'request_id': request_id})
                return JsonResponse({'error': str(e)})

        # Добавляем пустую строку между группами логов для разных URL
        logger.info("\n")

    if not all_last_urls:
        logger.info(f"[{request_id}] Все обновлено, новостей не найдено", extra={'request_id': request_id})
        return JsonResponse({'message': 'Новости обновлены'})  # Return the message instead of last_urls
    else:
        logger.info(f"[{request_id}] Последние найденные URL: {all_last_urls}", extra={'request_id': request_id})
        return JsonResponse({'last_urls': all_last_urls if all_last_urls else []})




