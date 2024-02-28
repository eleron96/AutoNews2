from django.urls import path
from .views import home, history_view, news_detail, dashboard_view, add_news, \
    add_news_form, delete_news  # Убедитесь, что импортировали add_news

urlpatterns = [
    path('', home, name='home'),
    path('history/', history_view, name='history'),
    path('news/<int:pk>/', news_detail, name='news_detail'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('add-news/', add_news, name='add_news'),  # Убедитесь, что добавили эту строку
    path('add-news-form/', add_news_form, name='add_news_form'),
    path('news/delete/<int:pk>/', delete_news, name='delete_news'),
    # Другие пути...
]
