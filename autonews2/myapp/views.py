from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages  # Импортируем messages из django.contrib

from .functions.api_handler import summarize_text
from .functions.forms import NewsForm

# Create your views here.
from django.shortcuts import render

from .models import News


def home(request):
    return render(request, 'myapp/home.html')

def history_view(request):
    news_list = News.objects.all().order_by('-date')  # Получаем все новости, отсортированные по дате
    return render(request, 'myapp/history.html', {'news_list': news_list})

def news_detail(request, pk):
    news = get_object_or_404(News, pk=pk)
    return render(request, 'myapp/news_detail.html', {'news': news})


def dashboard_view(request):
    return render(request, 'myapp/dashboard.html')  # Указываем правильный путь к шаблону

def add_news_form(request):
    form = NewsForm()  # Пустая форма
    return render(request, 'myapp/add_news_form.html', {'form': form})

@require_POST
def add_news(request):
    form = NewsForm(request.POST)
    if form.is_valid():
        new_news = form.save(commit=False)  # Сохраняем форму без коммита в базу данных
        # Обработка содержимого новости
        original_content = new_news.content
        print(original_content)
        summarized_content = summarize_text(original_content, new_news.author)
        new_news.content = summarized_content  # Замена оригинального контента на суммаризированный
        new_news.save()  # Теперь сохраняем новость с суммаризированным контентом
        messages.success(request, 'Новость успешно добавлена')
        return redirect('history')  # Или куда вы хотите перенаправить пользователя после добавления новости
    else:
        # Если форма невалидна, вернуть пользователя обратно на страницу формы
        print(form.errors)
        messages.error(request, 'Ошибка добавления новости')
        return redirect('home')  # Используйте ваш URL или имя view для страницы добавления новости

@require_POST  # Убедитесь, что этот вид может быть вызван только через POST-запрос
def delete_news(request, pk):
    news = get_object_or_404(News, pk=pk)
    news.delete()
    return redirect('history')  # Правильное название
