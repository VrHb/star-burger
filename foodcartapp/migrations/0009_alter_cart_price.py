# Generated by Django 3.2.15 on 2023-01-27 11:29

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0008_auto_20230127_1124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='цена'),
        ),
    ]
