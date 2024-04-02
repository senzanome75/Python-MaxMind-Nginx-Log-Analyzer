import csv
import geoip2.database
import re

# Percorso al file di log di nginx
log_file_path = './ingegnerealbano.com.access.log'

# Definizione del formato del log combined di nginx
log_pattern = re.compile(r'(?P<ip>\S+) \S+ \S+ \[(?P<datetime>[^\]]+)\] (?P<domain>\S+) "(?P<method>\S+) (?P<url>\S+) \S+" (?P<status>\d{3}) (?P<size>\S+) "(?P<referrer>[^"]*)" "(?P<useragent>[^"]*)"')

# Definisci il nome del file CSV
csv_filename = './ingegnerealbano.com.access.log.csv'

# Funzione per analizzare una riga del log
def parse_log_line(line):
    match = log_pattern.match(line)
    if match:
        return match.groupdict()
    else:
        return None

# Lista che conterrà tutti i dati analizzati
log_data_list = []

# Leggere il file di log e analizzare ogni riga
with open(log_file_path, 'r') as file:
    for line in file:
        log_data = parse_log_line(line)
        if log_data:
            with geoip2.database.Reader('GeoLite2-City.mmdb') as reader:
                response = reader.city(log_data['ip'])
                log_data.update({'city': response.city.name})
                log_data.update({'postalcode': response.postal.code})
                log_data.update({'latitude': response.location.latitude})
                log_data.update({'longitude': response.location.longitude})
            log_data_list.append(log_data)

# Se non ci sono dati nel file di log, esci dallo script
if not log_data_list:
    print("Nessun dato nel file di log.")
    exit()

# Definisci gli header del CSV basandoti sulle chiavi del primo dizionario nella lista
fieldnames = log_data_list[0].keys()

# Apre il file CSV in modalità scrittura
with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Scrivi l'header del CSV
    writer.writeheader()

    # Scrivi ogni riga del dizionario come una riga nel CSV
    for row in log_data_list:
        writer.writerow(row)

print("CSV generato con successo:", csv_filename)
