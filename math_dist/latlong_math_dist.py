import requests
from collections import namedtuple
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import random
from datetime import datetime, timedelta
from math import cos, asin, sqrt, pi

# Estrutura auxiliar para passar coordenadas tipadas
Coordenadas = namedtuple("Coordenadas", "latitude longitude")

# inicia o geolocator do geopy
geolocator = Nominatim(user_agent="GetDistanceBetweenCeps" + str(random.randint(0,100000)))
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

def format_endereco(endereco, sem_logradouro=False):
    fe_start_gmt_minus_3_time = datetime.utcnow() + timedelta(hours=-3)

    logradouro = endereco['street'] + ", "
    if sem_logradouro:
        logradouro = ''

    fe_end_gmt_minus_3_time = datetime.utcnow() + timedelta(hours=-3)
    fe_exec_time = fe_end_gmt_minus_3_time - fe_start_gmt_minus_3_time
    print(f"format_endereco execution time: {fe_exec_time}")
    return logradouro + endereco['neighborhood'] + ", " + endereco['city'] + " - " + endereco['state']

def address_from_cep(cep: str):
    afc_start_gmt_minus_3_time = datetime.utcnow() + timedelta(hours=-3)
    # busca o endereco ou coordenada pelo CEP
    response = requests.get(f'https://brasilapi.com.br/api/cep/v2/{cep}') 
    
    # caso a request não dê certo, puxa a mensagem de erro e mostra. Se não tiver mensagem, mostra "api error"
    if response.status_code != 200:
        err = response.json() 
        raise Exception(f"could not find CEP! Error: {err.get('message', 'api error')}")

    endereco = response.json()
    
    # Pega as informações de coordenadas direto da brasilapi se estiverem presentes. 
    # Muitas vezes não está, então retorna None quando for esse caso
    coordenadas = endereco.get('location', {}).get('coordinates', None)

    # removendo conteúdo dos correios indicando qual é o lado da rua pelo CEP
    endereco['street'] = endereco['street'].split(" lado ")[0] 

    afc_end_gmt_minus_3_time = datetime.utcnow() + timedelta(hours=-3)
    afc_exec_time = afc_end_gmt_minus_3_time - afc_start_gmt_minus_3_time
    print(f"address_from_cep execution time: {afc_exec_time}")
    # formata o endereço para ficar apropriado apra o geopy
    return endereco, coordenadas


def lat_long_from_cep(cep: str) -> Coordenadas:
    llfc_start_gmt_minus_3_time = datetime.utcnow() + timedelta(hours=-3)
    # busca CEP e faz um catch exception caso a request não tenha funcionado como esperado
    try:
        endereco, coord = address_from_cep(cep)
    except Exception as e:
        print(e)
        return None, None

    # Se as coordenadas estiverem presentes pela BrasilAPI, use-as. Caso contrário, busque no Geopy pelo enderedeço
    if coord and len(coord) > 0:
        location = Coordenadas(**coord)
    else:
        geopy_loc = geocode(format_endereco(endereco))
        
        # tentando novamente só com o bairro ao invés da rua quando não achar
        if not geopy_loc:
            geopy_loc = geocode(format_endereco(endereco, sem_logradouro=True))

        location = geopy_loc.point if geopy_loc else None

    if not location:
        print(f"both brasilAPI and geopy failed to find location for CEP: {cep}")
        return None, None

    llfc_end_gmt_minus_3_time = datetime.utcnow() + timedelta(hours=-3)
    llfc_exec_time = llfc_end_gmt_minus_3_time - llfc_start_gmt_minus_3_time
    print(f"lat_long_from_cep execution time: {llfc_exec_time}")
    return location.latitude, location.longitude


def distance(lat1, long1, lat2, long2):
    r = 6371 # km
    p = pi / 180

    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((long2-long1)*p))/2
    dist = 2 * r * asin(sqrt(a))
    return dist

