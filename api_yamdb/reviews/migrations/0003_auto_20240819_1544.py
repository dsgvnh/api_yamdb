# Generated by Django 3.2 on 2024-08-19 12:44

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_auto_20240816_1511'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='confirmation_code',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(error_messages={'blank': 'Заполните поле Username', 'unique': 'Такой username уже существует'}, max_length=150, unique=True, validators=[django.core.validators.RegexValidator(message='Неверный формат Username', regex='^[\\w.@+-]+\\Z'), django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(150)]),
        ),
    ]
