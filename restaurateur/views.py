from datetime import datetime
import itertools
from pprint import pprint

from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Subquery, OuterRef
from django.conf import settings

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from geopy import distance

from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem
from locations.models import Location
from locations.views import fetch_coordinates


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, 'login.html', context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect('restaurateur:RestaurantView')
                return redirect('start_page')

        return render(request, 'login.html', context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {
            item.restaurant_id: item.availability for item in product.menu_items.all()
        }
        ordered_availability = [
            availability.get(restaurant.id, False) for restaurant in restaurants
        ]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name='products_list.html', context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name='restaurants_list.html', context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = list(Order.objects.count_order_price() \
        .prefetch_related('cart_items').exclude(status='done') \
        .order_by('-status'))
    restaurant_items =  RestaurantMenuItem.objects.select_related('product', 'restaurant')
    location_objects = Location.objects.all()
    locations = {location.address: (location.lon, location.lat) for location in location_objects}
    orders_with_restaurants = []
    for order in orders:
        order_products = order.cart_items.values_list('product__id', flat=True)
        order_restaurants = restaurant_items.filter(product__in=order_products, availability=True).distinct().values('restaurant__name', 'restaurant__address')
        order_coordinates = locations.get(order.address)
        if not order_coordinates:
            lon, lat = fetch_coordinates(
                settings.YANDEX_GEO_API_KEY,
                order.address
            )
            location = Location.objects.create(
                address=order.address,
                lon=lon,
                lat=lat,
                query_at=datetime.now()
            )
            order_coordinates = (location.lon, location.lat)
        restaurants_with_distance_to_order = []
        for restaurant in order_restaurants:
            restaurant_coordinates = locations.get(restaurant['restaurant__address'])
            if not restaurant_coordinates:
                lon, lat = fetch_coordinates(
                    settings.YANDEX_GEO_API_KEY,
                    restaurant['restaurant__address']
                )
                location = Location.objects.create(
                    address=restaurant['restaurant__address'],
                    lon=lon,
                    lat=lat,
                    query_at=datetime.now()
                )
                restaurant_coordinates = (location.lon, location.lat)
            try:
                distance_to_order = distance.distance(
                    order_coordinates,
                    restaurant_coordinates
                ).km
                distance_to_order = f'{round(distance_to_order, 3)} км'
            except ValueError:
                distance_to_order = '0 км'
            restaurants_with_distance_to_order.append(
                {
                    "name": restaurant['restaurant__name'],
                    "distance_to_order": distance_to_order
                }
            )
        orders_with_restaurants.append(
            {
                'order': order, 
                'restaurants': restaurants_with_distance_to_order 
            }
        )
    return render(request, template_name='order_items.html', context={
        'order_items': orders_with_restaurants
    })
