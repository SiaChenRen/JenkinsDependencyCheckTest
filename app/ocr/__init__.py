import requests
import json

from flask import current_app as app

class Tesseract():
    url = app.config["TESSERACT_URL"]
    api_key = app.config["TESSERACT_API_KEY"]

    def send_ocr(self, file):
        post_data = {
            "API_KEY": self.api_key,
        }

        files = { "file" : file }

        result = requests.post(self.url, data=post_data, files=files)
        response = json.loads(result.text)

        return response
