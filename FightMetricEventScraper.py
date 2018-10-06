import csv
from bs4 import BeautifulSoup
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=25))

events = []
fights = []

url = "http://www.fightmetric.com/statistics/events/completed?page=all"
r = s.get(url)
soup = BeautifulSoup(r.text, "html.parser")
table = soup.find('table', attrs={'class': 'b-statistics__table-events'})
table_body = table.find('tbody')
rows = table_body.find_all('tr')[1:]

i = 0
for row in rows:
    # Get data
    cols = row.find_all('td')
    name_and_date = cols[0].find('i')
    event_name = name_and_date.find('a').text.strip()
    event_url = name_and_date.find('a').get('href')
    event_date = name_and_date.find('span').text.strip()
    event_location = cols[1].text.strip()

    # Only build and append dict if event was in the past
    past = datetime.strptime(event_date, "%B %d, %Y")
    present = datetime.now()

    if past.date() < present.date():
        # Build dict
        event = {
            "id" : i,
            "name" : event_name,
            "url" : event_url,
            "date" : event_date,
            "location" : event_location
        }

        events.append(event)
        i += 1

# Get fight urls
print("Parsing fights")

i = 0
j = 0
for event in events:
    print("    Parsing fights from event " + str(i))
    event_url = event["url"]
    r = s.get(event_url)
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find('table', attrs={'class': 'b-fight-details__table'})
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        fight_url = row.get('data-link')
        fight = {
            "id" : j,
            "url" : fight_url,
            "event_id" : event["id"]
        }
        fights.append(fight)
        j += 1
    i += 1

# Write to CSV
print("Writing csv files")

def write_csv_file(file_name, dict):
    file = open(file_name, 'w', newline="")
    keys = dict[0].keys()
    writer = csv.DictWriter(file, keys)
    writer.writeheader()
    writer.writerows(dict)

write_csv_file('stats/FightMetricEvents.csv', events)
write_csv_file('stats/FightMetricFights.csv', fights)