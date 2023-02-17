from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.templatetags.static import static

from phonenumber_field.serializerfields import PhoneNumberField

from rest_framework.decorators import api_view
from rest_framework.fields import ListField
from rest_framework.response import Response
from rest_framework.serializers import Serializer, ModelSerializer, CharField, IntegerField


from .models import Product
from .models import Order
from .models import CartItem


class OrderSerializer(ModelSerializer):
    products = ListField(allow_empty=False, write_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'firstname',
            'lastname',
            'phonenumber',
            'address',
            'products'
        ]



class ProductSerializer(Serializer):
    product = IntegerField(min_value=1)
    quantity = IntegerField()


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()
    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def orders_list_api(request):
    orders = Order.objects.all()
    dumped_orders = []
    for order in orders:
        dumped_order = {
            'id': order.id,
            'firstname': order.firstname,
            'lastname': order.lastname,
            'phonenumber': order.phonenumber,
            'address': order.address
        }
        dumped_orders.append(dumped_order)
    return JsonResponse(dumped_orders, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@transaction.atomic
@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    firstname = request.data['firstname']
    lastname = request.data['lastname']
    phonenumber = request.data['phonenumber']
    address = request.data['address']
    order = Order.objects.create(
        firstname=firstname,
        lastname=lastname,
        phonenumber=phonenumber,
        address=address,
    )
    serialized_order = OrderSerializer(order).data
    products = request.data['products']
    items = [] 
    for product in products:
        serializer = ProductSerializer(data=product)
        serializer.is_valid(raise_exception=True)
        product_from_db = Product.objects.get(id=product['product'])
        items.append(
        CartItem(
            order=order,
            product=product_from_db,
            amount=product['quantity'],
            price=product_from_db.price
            )
        )
    CartItem.objects.bulk_create(items)
    return Response(serialized_order)
