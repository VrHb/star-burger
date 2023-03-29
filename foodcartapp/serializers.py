from rest_framework.fields import ListField
from rest_framework.serializers import Serializer, ModelSerializer, IntegerField

from .models import Order


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
