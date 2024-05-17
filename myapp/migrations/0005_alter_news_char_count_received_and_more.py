# Generated by Django 5.0.2 on 2024-05-16 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_news_char_count_received_news_char_count_requested_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='char_count_received',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='news',
            name='char_count_requested',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='news',
            name='model_version',
            field=models.CharField(default='Данные отсутствуют', max_length=50),
        ),
    ]