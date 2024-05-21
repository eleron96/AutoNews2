from django.db import models

class News(models.Model):
    author = models.CharField(max_length=100)
    link = models.URLField()
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_at = models.DateTimeField(auto_now_add=True)
    model_version = models.CharField(max_length=50, default="Данные отсутствуют")  # Версия модели
    char_count_requested = models.IntegerField(default=0)  # Запрошенное количество символов
    char_count_received = models.IntegerField(default=0)  # Полученное количество символов

class URL(models.Model):
    address = models.URLField(max_length=200, unique=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title
