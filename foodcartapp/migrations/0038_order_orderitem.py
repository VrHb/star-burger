# Generated by Django 3.2.15 on 2023-01-18 10:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0037_auto_20210125_1833'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, verbose_name='Имя покупателя')),
                ('lastname', models.CharField(max_length=140, verbose_name='Фамилия покупателя')),
                ('address', models.CharField(max_length=100, verbose_name='Адрес покупателя')),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказы',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(verbose_name='Количество')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='orders', to='foodcartapp.order', verbose_name='Заказ')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='products', to='foodcartapp.product', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'Товар',
                'verbose_name_plural': 'Элементы заказа',
                'unique_together': {('order', 'product')},
            },
        ),
    ]
