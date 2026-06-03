import requests


def buscar_cep(cep: str):# Melhorar tratamento de erros.
    url_api= f"https://cep.awesomeapi.com.br/json/{cep}"
    resposta = requests.get(url_api, timeout=10)
    return resposta.json()

def buscar_tempo(lat: float, lng: float):#Melhorar tratamento de erros
    url_api = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&daily=precipitation_probability_max&current=temperature_2m,is_day&timezone=America%2FSao_Paulo"
    resposta = requests.get(url_api, timeout=10)
    return resposta.json()

print(buscar_tempo(-23.44099,-46.91242))
