# Generated by Django 3.2.15 on 2023-02-14 14:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='query_date',
            new_name='query_at',
        ),
    ]