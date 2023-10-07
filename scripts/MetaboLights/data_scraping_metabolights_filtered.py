import requests
import json
from ftplib import FTP

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

# Funzione per ottenere l'elenco delle cartelle dal server FTP
def get_folder_list(server, folder):
    ftp = FTP(server)
    ftp.login()
    folder_list = []
    ftp.retrlines('NLST ' + folder, folder_list.append)
    ftp.quit()
    return folder_list

# Indirizzo del server FTP e cartella base
server = "ftp.ebi.ac.uk"
base_folder = "/pub/databases/metabolights/studies/public/"

# Ottieni l'elenco delle cartelle dal server FTP
folder_list = get_folder_list(server, base_folder)
print(len(folder_list))

# Scrivi i dati nel file di output
with open('output_filt.txt', 'w') as output_file:
    for folder_name in folder_list:
        mtbls_number = folder_name.split('/')[-1]
        url = f'https://www.ebi.ac.uk/metabolights/ws/studies/{mtbls_number}/s_{mtbls_number}.txt'
        data = get_data(url)
        output_file.write(f'{mtbls_number}, {data}\n')
        print(f'{url}, {data}')
