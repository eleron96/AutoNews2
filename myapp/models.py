from django.db import models

class News(models.Model):
    author = models.CharField(max_length=100)
    link = models.URLField()
    title = models.CharField(max_length=200)
    content = models.TextField()
    # date = models.DateField(auto_now_add=True)  # Добавьте это поле
    published_at = models.DateTimeField(
        auto_now_add=True)  # Замените 'date' на это поле

    def __str__(self):
        return self.title