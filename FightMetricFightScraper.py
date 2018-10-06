import csv
from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=25))


def soup_get_fighter_details(e):
    result = e.find('i', attrs={'class': 'b-fight-details__person-status'}).text.strip()
    fighter_nickname = e.find('p', attrs={'class': 'b-fight-details__person-title'}).text.strip()
    h3 = e.find('h3', attrs={'class': 'b-fight-details__person-name'})
    fighter_name = h3.text.strip()
    if h3.find('a') is not None:
        fighter_url = h3.find('a').get('href')
    else:
        fighter_url = ""
    return fighter_name, fighter_nickname, fighter_url, result


def add_fighter_if_not_duplicate(name, nickname, url):
    global fighter_id

    for fighter in fighters:
        if fighter['name'] == name and fighter['nickname'] == nickname and fighter['url'] == url:
            return fighter['id']

    # Fighter not found, add it
    id = fighter_id
    fighter = {
        "id": id,
        "name": name,
        "nickname": nickname,
        "url": url
    }
    fighters.append(fighter)
    fighter_id += 1
    return id


def parse_fight_table_cols(cols):
    data = []
    for col in cols:
        col_data = []
        stats = col.find_all('p')
        for stat in stats:
            val = stat.text.strip()
            col_data.append(val)
        data.append(col_data)
    return data


def parse_x_of_y_string(s):
    return s.split(" of ")

fighter_id = 0
fighters = []
fights = []

f = open('stats/FightMetricFights.csv', newline='')
reader = csv.reader(f, delimiter=',')
headers = next(reader)

for row in reader:
    fight = {
        "id": row[1],
        "url": row[0],
    }
    fights.append(fight)

output = open('stats/FightMetricFightsData.csv', 'w', newline="")
keys = [
   'fighter2_sig_strikes_ground',
   'fighter1_submission_attempts',
   'fighter2_sig_strikes_clinch_attempt',
   'fighter1_sig_strikes_clinch',
   'fighter2_takedowns',
   'fighter1_sig_strikes_head_attempt',
   'fighter1_takedowns_attempt',
   'fighter1_sig_strikes_distance',
   'fighter1_total_strikes',
   'url',
   'fighter1_sig_strikes_attempt',
   'fighter2_sig_strikes_body',
   'fighter1_sig_strikes',
   'fighter2_sig_strikes_leg',
   'result',
   'fighter1',
   'fighter1_sig_strikes_leg_attempt',
   'fighter2_sig_strikes',
   'fighter2_takedowns_attempt',
   'fighter1_sig_strikes_distance_attempt',
   'fighter2_total_strikes',
   'fighter2',
   'fighter2_sig_strikes_head_attempt',
   'fighter2_pass',
   'fighter1_sig_strikes_body_attempt',
   'referee',
   'fighter2_sig_strikes_head',
   'fighter1_sig_strikes_ground',
   'fighter1_sig_strikes_clinch_attempt',
   'fighter2_sig_strikes_leg_attempt',
   'fighter2_knockdowns',
   'fighter1_sig_strikes_leg',
   'fighter1_knockdowns',
   'fighter1_rev',
   'fighter1_sig_strikes_head',
   'fighter2_rev',
   'fighter2_sig_strikes_body_attempt',
   'format',
   'fighter2_total_strikes_attempt',
   'fighter2_sig_strikes_clinch',
   'fighter1_sig_strikes_ground_attempt',
   'fighter2_sig_strikes_ground_attempt',
   'fighter2_sig_strikes_attempt',
   'fighter1_takedowns',
   'fighter2_sig_strikes_distance_attempt',
   'fighter2_sig_strikes_distance',
   'fighter2_submission_attempts',
   'fighter1_total_strikes_attempt',
   'id',
   'fighter1_sig_strikes_body',
   'time',
   'round',
   'fighter1_pass'
]
writer = csv.DictWriter(output, keys)
writer.writeheader()

fight_count = 0
for fight in fights:
    fight_url = fight["url"]
    print("Processing fight " + str(fight_count))
    fight_count += 1
    r = s.get(fight_url)
    soup = BeautifulSoup(r.text, "html.parser")
    soup_fighters = soup.find_all('div', attrs={'class': 'b-fight-details__person'})

    fighter1, fighter1_nickname, fighter1_url, fight_result = soup_get_fighter_details(soup_fighters[0])
    fight["fighter1"] = add_fighter_if_not_duplicate(fighter1, fighter1_nickname, fighter1_url)
    fighter2, fighter2_nickname, fighter2_url, _ = soup_get_fighter_details(soup_fighters[1])
    fight["fighter2"] = add_fighter_if_not_duplicate(fighter2, fighter2_nickname, fighter2_url)
    fight["result"] = fight_result

    soup_details = soup.find_all('i', attrs={'class': 'b-fight-details__text-item'})
    for detail in soup_details:
        detail_text = detail.text
        if "Round:" in detail_text:
            fight["round"] = detail_text.replace("Round:", "").strip()
        elif "Time:" in detail_text:
            fight["time"] = detail_text.replace("Time:", "").strip()
        elif "Time format:" in detail_text:
            fight["format"] = detail_text.replace("Time format:", "").strip()
        elif "Referee:" in detail_text:
            fight["referee"] = detail_text.replace("Referee:", "").strip()

    soup_tables = soup.find_all('table', attrs={'style': 'width: 745px'})

    if len(soup_tables) >= 2:

        # Fight totals

        totals_table = soup_tables[0]
        table_body = totals_table.find('tbody')
        row = table_body.find('tr')
        cols = row.find_all('td')
        cols = [cols[1], cols[2], cols[4], cols[5], cols[7], cols[8], cols[9]]
        totals_data = parse_fight_table_cols(cols)
        assert(len(totals_data) == 7)

        # 0: Knockdowns
        fight["fighter1_knockdowns"] = totals_data[0][0]
        fight["fighter2_knockdowns"] = totals_data[0][1]

        # 1: Significant strikes
        fighter1_sig_strikes = parse_x_of_y_string(totals_data[1][0])
        fight["fighter1_sig_strikes"] = fighter1_sig_strikes[0]
        fight["fighter1_sig_strikes_attempt"] = fighter1_sig_strikes[1]

        fighter2_sig_strikes = parse_x_of_y_string(totals_data[1][1])
        fight["fighter2_sig_strikes"] = fighter2_sig_strikes[0]
        fight["fighter2_sig_strikes_attempt"] = fighter2_sig_strikes[1]

        # 2: Total strikes
        fighter1_total_strikes = parse_x_of_y_string(totals_data[2][0])
        fight["fighter1_total_strikes"] = fighter1_total_strikes[0]
        fight["fighter1_total_strikes_attempt"] = fighter1_total_strikes[1]

        fighter2_total_strikes = parse_x_of_y_string(totals_data[2][1])
        fight["fighter2_total_strikes"] = fighter2_total_strikes[0]
        fight["fighter2_total_strikes_attempt"] = fighter2_total_strikes[1]

        # 3: Takedowns
        fighter1_takedowns = parse_x_of_y_string(totals_data[3][0])
        fight["fighter1_takedowns"] = fighter1_takedowns[0]
        fight["fighter1_takedowns_attempt"] = fighter1_takedowns[1]

        fighter2_takedowns = parse_x_of_y_string(totals_data[3][1])
        fight["fighter2_takedowns"] = fighter2_takedowns[0]
        fight["fighter2_takedowns_attempt"] = fighter2_takedowns[1]

        # 4: Submission attempts
        fight["fighter1_submission_attempts"] = totals_data[4][0]
        fight["fighter2_submission_attempts"] = totals_data[4][1]

        # 5: Pass guard
        fight["fighter1_pass"] = totals_data[5][0]
        fight["fighter2_pass"] = totals_data[5][1]

        # 6: Reverse position
        fight["fighter1_rev"] = totals_data[6][0]
        fight["fighter2_rev"] = totals_data[6][1]

        # Fight significant strikes

        sig_strikes_table = soup_tables[1]
        table_body = sig_strikes_table.find('tbody')
        row = table_body.find('tr')
        cols = row.find_all('td')[3:]
        sig_strikes_data = parse_fight_table_cols(cols)
        assert(len(sig_strikes_data) == 6)

        # 0: Head
        fighter1_sig_strikes_head = parse_x_of_y_string(sig_strikes_data[0][0])
        fight["fighter1_sig_strikes_head"] = fighter1_sig_strikes_head[0]
        fight["fighter1_sig_strikes_head_attempt"] = fighter1_sig_strikes_head[1]

        fighter2_sig_strikes_head = parse_x_of_y_string(sig_strikes_data[0][1])
        fight["fighter2_sig_strikes_head"] = fighter2_sig_strikes_head[0]
        fight["fighter2_sig_strikes_head_attempt"] = fighter2_sig_strikes_head[1]

        # 1: Body
        fighter1_sig_strikes_body = parse_x_of_y_string(sig_strikes_data[1][0])
        fight["fighter1_sig_strikes_body"] = fighter1_sig_strikes_body[0]
        fight["fighter1_sig_strikes_body_attempt"] = fighter1_sig_strikes_body[1]

        fighter2_sig_strikes_body = parse_x_of_y_string(sig_strikes_data[1][1])
        fight["fighter2_sig_strikes_body"] = fighter2_sig_strikes_body[0]
        fight["fighter2_sig_strikes_body_attempt"] = fighter2_sig_strikes_body[1]

        # 2: Leg
        fighter1_sig_strikes_leg = parse_x_of_y_string(sig_strikes_data[2][0])
        fight["fighter1_sig_strikes_leg"] = fighter1_sig_strikes_leg[0]
        fight["fighter1_sig_strikes_leg_attempt"] = fighter1_sig_strikes_leg[1]

        fighter2_sig_strikes_leg = parse_x_of_y_string(sig_strikes_data[2][1])
        fight["fighter2_sig_strikes_leg"] = fighter2_sig_strikes_leg[0]
        fight["fighter2_sig_strikes_leg_attempt"] = fighter2_sig_strikes_leg[1]

        # 3: Distance
        fighter1_sig_strikes_distance = parse_x_of_y_string(sig_strikes_data[3][0])
        fight["fighter1_sig_strikes_distance"] = fighter1_sig_strikes_distance[0]
        fight["fighter1_sig_strikes_distance_attempt"] = fighter1_sig_strikes_distance[1]

        fighter2_sig_strikes_distance = parse_x_of_y_string(sig_strikes_data[3][1])
        fight["fighter2_sig_strikes_distance"] = fighter2_sig_strikes_distance[0]
        fight["fighter2_sig_strikes_distance_attempt"] = fighter2_sig_strikes_distance[1]

        # 4: Clinch
        fighter1_sig_strikes_clinch = parse_x_of_y_string(sig_strikes_data[4][0])
        fight["fighter1_sig_strikes_clinch"] = fighter1_sig_strikes_clinch[0]
        fight["fighter1_sig_strikes_clinch_attempt"] = fighter1_sig_strikes_clinch[1]

        fighter2_sig_strikes_clinch = parse_x_of_y_string(sig_strikes_data[4][1])
        fight["fighter2_sig_strikes_clinch"] = fighter2_sig_strikes_clinch[0]
        fight["fighter2_sig_strikes_clinch_attempt"] = fighter2_sig_strikes_clinch[1]

        # 5: Ground
        fighter1_sig_strikes_ground = parse_x_of_y_string(sig_strikes_data[5][0])
        fight["fighter1_sig_strikes_ground"] = fighter1_sig_strikes_ground[0]
        fight["fighter1_sig_strikes_ground_attempt"] = fighter1_sig_strikes_ground[1]

        fighter2_sig_strikes_ground = parse_x_of_y_string(sig_strikes_data[5][1])
        fight["fighter2_sig_strikes_ground"] = fighter2_sig_strikes_ground[0]
        fight["fighter2_sig_strikes_ground_attempt"] = fighter2_sig_strikes_ground[1]

    writer.writerow(fight)

# Write to CSV
print("Writing csv files")

def write_csv_file(file_name, dict):
    file = open(file_name, 'w', newline="")
    keys = dict[0].keys()
    writer = csv.DictWriter(file, keys)
    writer.writeheader()
    writer.writerows(dict)

write_csv_file('stats/FightMetricFighters.csv', fighters)