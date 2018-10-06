import csv
from bs4 import BeautifulSoup
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=25))

fighters = []

f = open('stats/FightMetricFighters.csv', newline='')
reader = csv.reader(f, delimiter=',')
headers = next(reader)

for row in reader:
    fighter = {
        "id": row[1],
        "name": row[2],
        "nickname": row[0],
        "url": row[3]
    }
    fighters.append(fighter)

output = open('stats/FightMetricFightersData.csv', 'w', newline="")
keys = [
    "id",
    "name",
    "nickname",
    "url",
    "height",
    "height_inches",
    "weight",
    "reach",
    "stance",
    "is_orthodox",
    "dob",
    "record",
    "record_wins",
    "record_losses",
    "record_draws"
]
writer = csv.DictWriter(output, keys)
writer.writeheader()

i = 0
for fighter in fighters:
    print("Parsing fighter " + str(i) + ": " + fighter["name"])
    fighter_url = fighter["url"]
    if len(fighter_url) > 0:
        r = s.get(fighter_url)
        soup = BeautifulSoup(r.text, "html.parser")
        stat_list = soup.find('div', attrs={'class': 'b-list__info-box b-list__info-box_style_small-width js-guide'}).find_all('li')
        for stat in stat_list:
            stat_text = stat.text.strip()
            if "Height:" in stat_text:
                height = stat_text.replace("Height:", "").strip()
                arr = height[:-1].split("' ")
                feet = arr[0]
                inches = arr[1]
                height_inches = int(feet) * 12 + int(inches)
                fighter["height"] = height
                fighter["height_inches"] = height_inches
            elif "Weight:" in stat_text:
                fighter["weight"] = stat_text.replace("Weight:", "").replace("lbs.", "").strip()
            elif "Reach:" in stat_text:
                fighter["reach"] = stat_text.replace("Reach:", "").replace('"', "").strip()
            elif "STANCE:" in stat_text:
                stance = stat_text.replace("STANCE:", "").strip()
                if stance == "Orthodox":
                    fighter["is_orthodox"] = 1
                else:
                    fighter["is_orthodox"] = 0
                fighter["stance"] = stance
            elif "DOB:" in stat_text:
                fighter["dob"] = stat_text.replace("DOB:", ""). strip()
        record = soup.find('span', attrs={'class': 'b-content__title-record'})
        record = record.text.replace("Record:", "").strip()
        record_parse = record.split(" ")[0].split("-")
        fighter["record"] = record
        fighter["record_wins"] = record_parse[0]
        fighter["record_losses"] = record_parse[1]
        fighter["record_draws"] = record_parse[2]

    writer.writerow(fighter)
    i += 1
