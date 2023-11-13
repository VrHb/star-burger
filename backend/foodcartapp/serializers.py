from rest_framework.serializers import ModelSerializer

from .models import Order, CartItem 


class ProductSerializer(ModelSerializer):

    class Meta:
        model = CartItem 
        fields = [
            'product',
            'quantity',
        ]

class OrderSerializer(ModelSerializer):
    products = ProductSerializer(many=True, write_only=True) 


    def create(self, validated_data):
        firstname = validated_data.get('firstname')
        lastname = validated_data.get('lastname')
        phonenumber = validated_data.get('phonenumber')
        address = validated_data.get('address')
        products = validated_data.get('products')
        order = Order.objects.create(
            firstname=firstname,
            lastname=lastname,
            phonenumber=phonenumber,
            address=address
        )
        items = []
        for product in products:
            items.append(
                CartItem(
                    order=order,
                    product=product['product'],
                    quantity=product['quantity'],
                    price=product['product'].price
                )
            )
        CartItem.objects.bulk_create(items)
        return order


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
