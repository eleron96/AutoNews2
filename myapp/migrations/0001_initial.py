# Generated by Django 5.0.6 on 2024-05-23 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.CharField(max_length=100)),
                ('link', models.URLField()),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('published_at', models.DateTimeField(auto_now_add=True)),
                ('model_version', models.CharField(default='Данные отсутствуют', max_length=50)),
                ('char_count_requested', models.IntegerField(default=0)),
                ('char_count_received', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='URL',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.URLField(unique=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]
