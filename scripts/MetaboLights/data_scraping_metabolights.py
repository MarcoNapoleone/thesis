import requests
from bs4 import BeautifulSoup
import json


# Funzione per ottenere il numero desiderato dalla pagina web
def get_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        rows = data.get('data', {}).get('rows', [])
        if rows:
            last_row = rows[-1]
            index_value = last_row.get('index')
            return index_value
    return "N/A"


# Scrivi i dati nel file di output
with open('output.txt', 'w') as output_file:
    for x in range(1, 10000):
        url = f'https://www.ebi.ac.uk/metabolights/ws/studies/MTBLS{x}/s_MTBLS{x}.txt'
        data = get_data(url)
        output_file.write(f'MTBLS{x}, {data}\n')
        print(f'MTBLS{x}, {data}')
