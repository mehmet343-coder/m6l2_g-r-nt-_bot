import json
import time
import requests
import base64
from PIL import Image
from io import BytesIO
from config import API_KEY, SECRET_KEY

class FusionBrainAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_pipeline(self):
        response = requests.get(self.URL + 'key/api/v1/pipelines', headers=self.AUTH_HEADERS)
        data = response.json()

        # Güvenli kontrol
        if not isinstance(data, list) or len(data) == 0:
            print("Pipeline listesi boş veya format hatalı:", data)
            return None

        return data[0]['id']

    def generate(self, prompt, pipeline, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'pipeline_id': (None, pipeline),
            'params': (None, json.dumps(params), 'application/json')
        }

        response = requests.post(self.URL + 'key/api/v1/pipeline/run', 
                                 headers=self.AUTH_HEADERS, 
                                 files=data)

        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(
                self.URL + 'key/api/v1/pipeline/status/' + request_id,
                headers=self.AUTH_HEADERS
            )

            data = response.json()

            if data.get('status') == 'DONE':
                return data['result']['files']

            attempts -= 1
            time.sleep(delay)

        return None

    def save_image(self, base64_string, file_path):
        decoded_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(decoded_data))

        # PNG olarak kayıt edilecek, RGBA sorun olmaz
        image.save(file_path)
        print(f"Görüntü kaydedildi: {file_path}")
