import requests
from .constans import *
from datetime import datetime
import os


def get_apod_filename():
    today = datetime.now().strftime('%Y-%m-%d')

    download_file = [file for file in os.listdir(API_DIR) if file.startswith(today)]
    if download_file:
        return download_file[0]
    try:
        params = {'api_key': API_KEY}
        response = requests.get(API_URL, params=params).json()
        media_url = response['url']
        media_type = response.get('media_type', 'image')

        if media_type == 'video':
            ext = '.mp4'
        else:
            ext = os.path.splitext(media_url)[1] or '.jpg'

        filename = f"{today}{ext}"
        filepath = os.path.join(API_DIR, filename)

        file_response = requests.get(media_url, stream=True)
        if file_response.status_code == 200:
            with open(filepath, 'wb') as file:
                file.write(file_response.content)
            return filename
        else:
            print(" Ошибка скачивания файла.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка NASA API: {e}")
        return None

    # params = {
    #     'api_key': API_KEY,
    # }
    #
    # if date:
    #     params['date'] = date
    #
    # try:
    #     response = requests.get(API_URL, params=params, timeout=10)
    #     response.raise_for_status()
    #     return response.json()
    # except requests.exceptions.RequestException as e:
    #     print(f"Ошибка NASA API: {e}")
    #     return None


def get_apod_data(date=None):
    params = {'api_key': API_KEY}
    if date:
        params['date'] = date
    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка NASA API: {e}")
        return None