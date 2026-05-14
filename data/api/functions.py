import requests
from .constans import *


def get_apod_data(date=None):
    params = {
        'api_key': API_KEY,
    }

    if date:
        params['date'] = date

    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка NASA API: {e}")
        return None