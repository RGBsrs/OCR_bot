import requests
from requests.models import Response

class OcrAPI:

    url = 'https://api.ocr.space/parse/image'

    def __init__(self, api_key:str = None):
        self.api_key = api_key

    def make_request(self, payload:dict = None, files = None) -> Response():
        self.payload = payload
        self.payload['apikey'] = self.api_key

        resp = requests.post(self.url, data=self.payload, files=files)
        
        return resp
