from loguru import logger
import requests
from config_data.config import API_KEY


api = {'X-RapidApi-Key': API_KEY, 'X-RapidAPI-Host': "hotels4.p.rapidapi.com"}


def request_api(url, params, headers):
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == requests.codes.ok:
            return response
        else:
            raise ConnectionError
    except requests.ConnectionError:
        print('Error')


@logger.catch()
def hotel_info(data: dict):
    id_hotel = data.get('property_id')
    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": id_hotel
    }
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "hotels4.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == requests.codes.ok:
            json_data = response.json()
            properties = json_data.get("data", {}).get("propertyInfo", {})

            if not properties:
                logger.error(f"Информации по id не найдено: {id_hotel}")
                return None

            name = properties.get('summary', {}).get('name', "")
            location = properties.get("summary", {}).get("location", {}).get("address", {}).get("addressLine", "")
            map_url = properties.get("summary", {}).get("location", {}).get("staticImage", {}).get("url", "")
            photos = properties.get('propertyGallery', {}).get('images', [])

            photo_urls = [photo.get('image', {}).get('url', '') for photo in photos]

            hotel_info_str = f"Название: {name}\nЛокация: {location}\nUrl: {map_url}"
            return hotel_info_str, photo_urls

        else:
            logger.error(f"Ошибка: {response.status_code}")
            return None
    except requests.ConnectionError:
        logger.error(f"Для id: {id_hotel}")
        return None