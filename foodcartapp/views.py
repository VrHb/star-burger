import json

from django.http import JsonResponse
from django.templatetags.static import static

from phonenumber_field.phonenumber import PhoneNumber

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


from .models import Product
from .models import Order 
from .models import Cart 



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
    firstname = request.data.get('firstname', None)
    if not firstname or not isinstance(firstname, str):
        return Response(
            {'Error': 'field firstname are empty or not str!'},
            status=status.HTTP_400_BAD_REQUEST
        )
    lastname = request.data.get('lastname', None)
    if not lastname or not isinstance(lastname, str):
        return Response(
            {'Error': 'field lastname are empty or not str!'},
            status=status.HTTP_400_BAD_REQUEST
        )
    phone = request.data.get('phonenumber', None)
    if not isinstance(phone, str) or not phone:
        return Response(
            {'Error': 'Phonenumber are empty or not str type!'},
            status=status.HTTP_400_BAD_REQUEST
        )
    parsed_phone = PhoneNumber.from_string(phone, region='RU')
    print(type(parsed_phone))
    if not parsed_phone.is_valid():
        return Response(
            {'Error': 'Phonenumber not correct!'},
            status=status.HTTP_400_BAD_REQUEST
        )
    address = request.data.get('address', None)
    if not address or not isinstance(address, str):
        return Response(
            {'Error': 'field address are empty or not str!'},
            status=status.HTTP_400_BAD_REQUEST
        )
    products = request.data.get('products', None)
    if not isinstance(products, list) or not products:
        return Response(
            {'Error': 'Products data are empty or not list type!'},
            status=status.HTTP_400_BAD_REQUEST
        )
    print(phone)
    order = Order.objects.create(
        firstname=firstname,
        lastname=lastname,
        phone=phone,
        address=address,
    )
    for product in products:
        try:
            product_from_db = Product.objects.get(pk=product['product'])
        except Product.DoesNotExist:
            return Response(
                {'Error': 'No product with this id!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Cart.objects.create(
            order=order,
            product=product_from_db,
            amount=product['quantity'],
        )
    return Response({"Status": "ok"}) 
