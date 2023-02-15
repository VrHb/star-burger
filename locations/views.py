import requests


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
