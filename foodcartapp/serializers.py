from rest_framework.fields import ListField
from rest_framework.serializers import Serializer, ModelSerializer, IntegerField

from .models import Order


class ProductSerializer(Serializer):
    product = IntegerField(min_value=1)
    quantity = IntegerField()


class OrderSerializer(ModelSerializer):
    products = ProductSerializer(many=True, read_only=True) 


    def create(self, validated_data):
        firstname = validated_data.get('firstname')
        lastname = validated_data.get('lastname')
        phonenumber = validated_data.get('phonenumber')
        address = validated_data.get('address')

        return Order.objects.create(
            firstname=firstname,
            lastname=lastname,
            phonenumber=phonenumber,
            address=address
        )


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

