from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages  # Импортируем messages из django.contrib
from django.views.decorators.csrf import csrf_protect


from .functions.api_handler import summarize_text
from .functions.forms import NewsForm

# Create your views here.
from django.shortcuts import render

from .models import News


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

    print('Обновленные настройки:')
    print('Модель:', engine_select)
    print('Количество символов:', char_count)

    # Сохраняем настройки в session
    request.session['engine_select'] = engine_select
    request.session['char_count'] = char_count

    messages.success(request, 'Настройки успешно обновлены')
    return redirect('settings')

# @require_POST
# def add_news(request):
#     form = NewsForm(request.POST)
#     if form.is_valid():
#         new_news = form.save(commit=False)  # Сохраняем форму без коммита в базу данных
#         # Обработка содержимого новости
#         original_content = new_news.content
#         print(original_content)
#         summarized_content = summarize_text(original_content, new_news.author)
#         new_news.content = summarized_content  # Замена оригинального контента на суммаризированный
#         new_news.save()  # Теперь сохраняем новость с суммаризированным контентом
#         messages.success(request, 'Новость успешно добавлена')
#         return redirect('history')  # Или куда вы хотите перенаправить пользователя после добавления новости
#     else:
#         # Если форма невалидна, вернуть пользователя обратно на страницу формы
#         print(form.errors)
#         messages.error(request, 'Ошибка добавления новости')
#         return redirect('home')  # Используйте ваш URL или имя view для страницы добавления новости

@require_POST
def add_news(request):
    form = NewsForm(request.POST)
    if form.is_valid():
        new_news = form.save(commit=False)
        engine_select = request.session.get('engine_select', 'gpt-3.5-turbo')
        char_count = request.session.get('char_count', 800)

        print('Используемая модель:', engine_select)  # Отладочное сообщение
        print('Количество символов:', char_count)  # Отладочное сообщение

        original_content = new_news.content
        summarized_content = summarize_text(original_content, new_news.author,
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
