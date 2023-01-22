from django.http import JsonResponse
from django.templatetags.static import static

from phonenumber_field.serializerfields import PhoneNumberField

from rest_framework.decorators import api_view
from rest_framework.fields import ListField
from rest_framework.response import Response
from rest_framework.serializers import Serializer, CharField, IntegerField


from .models import Product
from .models import Order 
from .models import Cart 


class OrderSerializer(Serializer):
    id = IntegerField(read_only=True)
    firstname = CharField()
    lastname = CharField()
    phonenumber = PhoneNumberField(region='RU')
    address = CharField()
    products = ListField(allow_empty=False, write_only=True)

    def create(self, validated_data):
        return Order.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.firstname = validated_data.get('fisrtname', instance.firstname)
        instance.lastname = validated_data.get('lastname', instance.lastname)
        instance.phonehumber = validated_data.get('phonenumber', instance.phonenumber)
        instance.products = validated_data.get('products', instance.products)
        instance.save()
        return instance

class ProductSerializer(Serializer):
    product = IntegerField(min_value=1, max_value=Product.objects.count())
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


@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    firstname = request.data.get('firstname', None)
    lastname = request.data.get('lastname', None)
    phonenumber = request.data.get('phonenumber', None)
    address = request.data.get('address', None)
    products = request.data.get('products', None)
    order = Order(
        firstname=firstname,
        lastname=lastname,
        phonenumber=phonenumber,
        address=address,
    )
    order.save()
    serialized_order = OrderSerializer(order).data
    for product in products:
        serializer = ProductSerializer(data=product)
        serializer.is_valid(raise_exception=True)
        product_from_db = Product.objects.get(id=product['product'])
        Cart.objects.create(
            order=order,
            product=product_from_db,
            amount=product['quantity'],
        )
    return Response(serialized_order) 
