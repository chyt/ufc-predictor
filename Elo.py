import csv
import operator

fights = []
fighters = []

# Process fighters

f = open('stats/FightMetricFighters.csv', newline='')
reader = csv.reader(f, delimiter=',')
headers = next(reader)

for row in reader:
    fighter = {}
    for i in range(0, len(row) - 1):
        fighter[str(headers[i])] = row[i]
    display_name = str(fighter["name"] + " (" + fighter["nickname"] + ")")
    fighter["display_name"] = display_name
    fighters.append(fighter)


# Process fights

f = open('stats/FightMetricFightsData.csv', newline='')
reader = csv.reader(f, delimiter=',')
headers = next(reader)

for row in reader:
    fight = {}
    for i in range(0, len(row) - 1):
        fight[str(headers[i])] = row[i]

    fight["fighter1"] = fighters[int(fight["fighter1"])]["display_name"]
    fight["fighter2"] = fighters[int(fight["fighter2"])]["display_name"]
    fights.append(fight)

print("Number of fighters: " + str(len(fighters)))
print("Number of fights: " + str(len(fights)))

# Initialize each fighter's elo to 1200 and number of fights to 0

elo = {}
number_of_fights = {}
for fighter in fighters:
    elo[fighter["display_name"]] = 1000
    number_of_fights[fighter["display_name"]] = 0

def get_k_value(number_of_fights):
    if number_of_fights < 3:
        return 200
    if number_of_fights < 6:
        return 150
    return 100

# Iterate through the fights, calculate elo after each fight

for fight in reversed(fights):
    fighter_1 = fight["fighter1"]
    fighter_2 = fight["fighter2"]

    fighter_1_elo = elo[fighter_1]
    fighter_2_elo = elo[fighter_2]

    fight["fighter1_before_elo"] = fighter_1_elo
    fight["fighter2_before_elo"] = fighter_2_elo

    # No contest, no change to elo
    if fight["result"] == "NC":
        fight["fighter1_after_elo"] = fighter_1_elo
        fight["fighter2_after_elo"] = fighter_2_elo
        continue

    # Draw or win, recalculate elo
    fighter_1_expected_outcome = 1 / (1 + 10 ** ((fighter_2_elo - fighter_1_elo) / 400))
    fighter_2_expected_outcome = 1 - fighter_1_expected_outcome

    fighter_1_number_of_fights = number_of_fights[fighter_1]
    fighter_2_number_of_fights = number_of_fights[fighter_2]

    fighter_1_k_value = get_k_value(fighter_1_number_of_fights)
    fighter_2_k_value = get_k_value(fighter_2_number_of_fights)

    if fight["result"] == "W":
        fighter_1_weight = 1
        fighter_2_weight = 0
    elif fight["result"] == "L":
        fighter_1_weight = 0
        fighter_2_weight = 1
    else: # fight was a draw
        fighter_1_weight = 0.5
        fighter_2_weight = 0.5

    fight["fighter1_after_elo"] = fighter_1_elo + fighter_1_k_value * (fighter_1_weight - fighter_1_expected_outcome)
    fight["fighter2_after_elo"] = fighter_2_elo + fighter_2_k_value * (fighter_2_weight - fighter_2_expected_outcome)

    elo[fighter_1] = fight["fighter1_after_elo"]
    elo[fighter_2] = fight["fighter2_after_elo"]

    """
    if fight["Fighter1"] == "Conor McGregor":
        print("win: " + str(elo[fighter_1]) + fighter_2)
    if fight["Fighter2"] == "Conor McGregor":
        print("loss: " + str(elo[fighter_2]) + fighter_1)
    """


print(elo['Conor McGregor ("The Notorious")'])
print(elo['Khabib Nurmagomedov ("The Eagle")'])

fighter_1_expected_outcome = 1 / (1 + 10 ** ((elo['Khabib Nurmagomedov ("The Eagle")'] - elo['Conor McGregor ("The Notorious")']) / 400))
fighter_2_expected_outcome = 1 - fighter_1_expected_outcome
print(fighter_1_expected_outcome)
print(fighter_2_expected_outcome)

sorted_elo = sorted(elo.items(), key=operator.itemgetter(1), reverse=True)
print(sorted_elo[:20])