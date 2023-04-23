import json
from pprint import pprint

import requests


def getPosition(city):
    url = f"https://geocode-maps.yandex.ru/1.x/?geocode={city}&apikey=8baeb8bf-32b8-42b5-bebc-e4cd7c21a8c5&format=json"

    headers = {
        'Cookie': '_yasc=67YURTc5Bu7+4YxMYlGZWMzbtDNhhJkU5I9e3/LMRm52p4VSvIacbqo+TQE=; i=83cOWTRqbR+vRTwHAwxwDBtr1F/XlcR+l8s7lnmzJTlMMEnO9u9LG4QHLZr5A0IoyrH06GiLG1AubniGCQNIQR+qJLs=; yandexuid=3267969091682028512'
    }

    response = requests.request("GET", url, headers=headers)

    data = response.text
    data = json.loads(data)
    return data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
    # return "56.90 34.78"

