from datetime import datetime

from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
from django.conf import settings

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

import requests
from geopy import distance

from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem
from locations.models import Location


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
    orders = Order.objects.count_order_price().exclude(status='done') \
        .order_by('-status')
    order_with_restaurants = []
    for order in orders:
        products = [
            item.product.id for item in order.cart_items.select_related('product').all()
        ]
        restaurants = RestaurantMenuItem.objects.filter(product__id__in=products) \
            .values('restaurant__name', 'restaurant__address') \
            .annotate(count_items=(Count('product__id'))) \
            .filter(count_items=len(products))
        try:
            location = Location.objects.get(address=order.address)
            order_coordinates = (location.lon, location.lat)
        except Location.DoesNotExist:
            lon, lat = fetch_coordinates(
                settings.YANDEX_GEO_API_KEY,
                order.address
            )
            location = Location.objects.create(
                address=order.address,
                lon=lon,
                lat=lat,
                query_date=datetime.now()
            )
            order_coordinates = (location.lon, location.lat)
        for restaurant in restaurants:
            try:
                location = Location.objects.get(address=restaurant['restaurant__address'])
                restaurant_coordinates = (location.lon, location.lat)
            except Location.DoesNotExist:
                lon, lat = fetch_coordinates(
                    settings.YANDEX_GEO_API_KEY,
                    restaurant.address
                )
                location = Location.objects.create(
                    address=restaurant['restaurant__address'],
                    lon=lon,
                    lat=lat,
                    query_date=datetime.now()
                )
                restaurant_coordinates = (location.lon, location.lat)
            restaurant['coordinates'] = restaurant_coordinates
            try:
                distance_to_order = distance.distance(
                    order_coordinates,
                    restaurant_coordinates
                ).km
                restaurant['distance_to_order'] = f'{round(distance_to_order, 3)} км'
            except ValueError:
                restaurant['distance_to_order'] = '0 км'
        order_with_restaurants.append(
            (order, sorted(
                restaurants,
                key=lambda restaurant: restaurant['distance_to_order']
                ))
        )
    return render(request, template_name='order_items.html', context={
        'order_items': order_with_restaurants
    })


def fetch_coordinates(apikey, address):
    base_url = 'https://geocode-maps.yandex.ru/1.x'
    response = requests.get(
        base_url,
        params={
            'geocode': address,
            'apikey': apikey,
            'format': 'json',
        }
    )
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']
    if not found_places:
        return (0, 0)
    most_reverant = found_places[0]
    lon, lat = most_reverant['GeoObject']['Point']['pos'].split(' ')
    return lon, lat
