from django.db import models
from django.db.models import F, Sum
from django.core.validators import MinValueValidator
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):


    def count_order_price(self):
        return self.annotate(
            order_price=Sum(
                F('cart_items__product__price') * F('cart_items__quantity')
            )
        )


    def get_done_orders(self):
        return self.exclude(status='done').select_related('chosen_restaurant') \
            .prefetch_related('cart_items__product') \
            .order_by('-status')


class Order(models.Model):
    ORDER_STATE_CHOICES = [
        ('accepted', 'Обрабатывается'),
        ('packing', 'Упаковывается'),
        ('delivery', 'Передан в доставку'),
        ('done', 'Выполнен')
    ]
    ORDER_PAYMENT_CHOICES = [
        ('clarify', 'Уточнить'),
        ('cash', 'Наличными'),
        ('card', 'Картой')
    ]
    firstname = models.CharField(
        'Имя покупателя',
        max_length=100,
        db_index=True
    )
    lastname = models.CharField(
        'Фамилия покупателя',
        max_length=140,
        db_index=True,
        )
    phonenumber = PhoneNumberField('Номер телефона')
    address = models.CharField('Адрес покупателя', max_length=100)
    status = models.CharField(
        'Статус',
        max_length=50,
        choices=ORDER_STATE_CHOICES,
        default='Обрабатывается',
        db_index=True
    )
    comment = models.TextField('Комментарий к заказу', blank=True)
    registered_at = models.DateTimeField(
        'Дата регистрации',
        default=timezone.now,
        blank=True,
        db_index=True
    )
    called_at = models.DateTimeField(
        'Дата звонка',
        null=True,
        blank=True,
        db_index=True
    )
    delivered_at = models.DateTimeField(
        'Дата доставки',
        null=True,
        blank=True,
        db_index=True
    )
    registered_at = models.DateTimeField(
        'Дата регистрации',
        default=timezone.now,
        blank=True,
        db_index=True
    )
    called_at = models.DateTimeField(
        'Дата звонка',
        null=True,
        blank=True,
        db_index=True
    )
    delivered_at = models.DateTimeField(
        'Дата доставки',
        null=True,
        blank=True,
        db_index=True
    )
    pay_method = models.CharField(
        'Способ оплаты',
        max_length=100,
        choices=ORDER_PAYMENT_CHOICES,
        default='Уточнить',
        db_index=True
    )
    chosen_restaurant = models.ForeignKey(
        Restaurant,
        verbose_name='Ресторан готовящий заказ',
        related_name='orders',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f"{self.firstname} {self.lastname} {self.address}"


class CartItem(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name='Заказ',
        related_name='cart_items',
        on_delete=models.CASCADE
        )
    product = models.ForeignKey(
        Product,
        verbose_name='Товар',
        related_name='cart_items',
        on_delete=models.CASCADE
        )
    quantity = models.IntegerField(
        'Количество',
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Элементы заказа'
        unique_together = [
            ['order', 'product']
        ]

    def __str__(self):
        return f"{self.product.name} {self.order}"
