# Generated by Django 3.2.15 on 2023-02-01 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0012_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, verbose_name='Комментарий к заказу'),
        ),
    ]
