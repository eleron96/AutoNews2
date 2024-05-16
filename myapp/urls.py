from django.urls import path
from .views import home, history_view, news_detail, dashboard_view, add_news, add_news_form, delete_news, update_settings

urlpatterns = [
    path('', home, name='home'),
    path('history/', history_view, name='history'),
    path('news/<int:pk>/', news_detail, name='news_detail'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('settings/', dashboard_view, name='settings'),  # Добавьте этот путь
    path('add-news/', add_news, name='add_news'),
    path('add-news-form/', add_news_form, name='add_news_form'),
    path('news/delete/<int:pk>/', delete_news, name='delete_news'),
    path('update-settings/', update_settings, name='update_settings'),
    # Другие пути...
]
