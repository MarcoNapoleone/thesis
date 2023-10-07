# Leggi il contenuto del file in una lista di tuple (MTBLS, numero)
with open('./output_filt.txt', 'r') as file:
    lines = file.readlines()
    data = [line.strip().split(', ') for line in lines]

# Ordina la lista di tuple in base al numero (la seconda colonna)
data.sort(key=lambda x: int(x[1]) if x[1] != 'N/A' else float('inf'))

# Scrivi il risultato ordinato in un nuovo file
with open('output_sorted.txt', 'w') as file:
    for item in data:
        file.write(f'{item[0]}, {item[1]}\n')
