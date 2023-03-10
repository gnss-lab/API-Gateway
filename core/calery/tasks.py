import json
import time

import httpx
from celery import shared_task
from fastapi import File


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5},
             name='university:get_upload_file')
def get_upload_file(self, file: bytes = File(...)):
    result = send_file(file)
    return result


def send_file(file: bytes = File(...)) -> dict:
    # time.sleep(10)
    # response_json = {"status": "ok"}

    # with open(file, "rb") as f:
    #     file_content = f.read()

    url = 'http://46.149.73.242:8000/uploadfile'
    # params = {'country': country}
    client = httpx.Client()
    response = client.post(url, files={"file": file})

    response_json = json.loads(response.text)

    return response_json
