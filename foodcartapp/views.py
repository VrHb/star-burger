import json

from django.http import JsonResponse
from django.templatetags.static import static

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
    firstname = request.data['firstname']
    lastname = request.data['lastname']
    address = request.data['address']
    products = request.data.get('products', None)
    if type(products) is not list or not products:
        return Response(
            {'Error': 'Products data are empty or not list type'},
            status=status.HTTP_400_BAD_REQUEST
        )
    order = Order.objects.create(
        firstname=firstname,
        lastname=lastname,
        address=address,
    )
    for product in products:
        Cart.objects.create(
            order=order,
            product=Product.objects.get(pk=product['product']),
            amount=product['quantity'],
            )
    return Response({"Status": "ok"}) 
