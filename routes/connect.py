from fastapi import APIRouter, Depends, status, Response, HTTPException
import requests
import json
from enum import Enum

class bbmModel(str, Enum):
    Pertamax_Turbo = "Pertamax Turbo"
    Pertamax = "Pertamax"
    Pertalite = "Pertalite"  

def get_bearer_token():
    url = 'https://motordhika.wonderfulisland-bafbc83c.centralus.azurecontainerapps.io/login'
    data = {"username": "admin", "password": "adminadmin"}
    response = requests.post(url, data=data)
    jsonresponse = response.json()
    bearertoken = str(jsonresponse['access_token'])
    return bearertoken

def format_get(url: str):
    link = url
    headers = {"Authorization": f'Bearer {get_bearer_token()}'}
    response = requests.get(link, headers=headers)
    jsonresponse = response.json()
    return jsonresponse

def get_bensin(jenis_motor: str, jangkauan_km_perhari: float, lokasi: str, jenis_bbm: bbmModel):
    url = f'https://motordhika.wonderfulisland-bafbc83c.centralus.azurecontainerapps.io/motors/harga-bulanan-bbm/{jenis_motor}?jangkauan_km_perhari={jangkauan_km_perhari}&lokasi={lokasi}&jenis_bbm={jenis_bbm}'
    return format_get(url)

  