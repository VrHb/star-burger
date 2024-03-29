from django.db import models



class Location(models.Model):
    address = models.CharField('Адрес места', max_length=200, unique=True)
    lat = models.DecimalField('Широта', max_digits=9, decimal_places=6, null=True)
    lon = models.DecimalField('Долгота', max_digits=9, decimal_places=6, null=True)
    query_at = models.DateTimeField('Дата запроса')
