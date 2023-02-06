# Generated by Django 3.2.15 on 2023-02-06 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=200, unique=True, verbose_name='Адрес места')),
                ('lat', models.DecimalField(decimal_places=6, max_digits=9, verbose_name='Широта')),
                ('lon', models.DecimalField(decimal_places=6, max_digits=9, verbose_name='Долгота')),
                ('query_date', models.DateTimeField(verbose_name='Дата запроса')),
            ],
        ),
    ]