from datetime import datetime
from django.conf import settings

import requests
from geopy import distance

from .models import Location


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
        return None 
    most_reverant = found_places[0]
    lon, lat = most_reverant['GeoObject']['Point']['pos'].split(' ')
    return lon, lat


def create_location_and_get_coordinates(address):
    try:
        lon, lat = fetch_coordinates(
            settings.YANDEX_GEO_API_KEY,
            address
        )
        location = Location.objects.create(
            address=address,
            lon=lon,
            lat=lat,
            query_at=datetime.now()
        )
        coordinates = (location.lat, location.lon)
        return coordinates
    except Exception:
        return None


def get_distance_to_order(restaurant_coordinates, order_coordinates):
    if not restaurant_coordinates or not order_coordinates:
        distance_to_order = '0 км'
        return distance_to_order
    distance_to_order = distance.distance(
            order_coordinates,
            restaurant_coordinates
    ).km
    distance_to_order = f'{round(distance_to_order, 3)} км'
    return distance_to_order
