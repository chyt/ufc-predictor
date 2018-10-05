import csv
import operator

fights = []
fighters = []

# Process fights

f = open('stats/Sherdog_Fights.csv', newline='')

reader = csv.reader(f, delimiter=',')
headers = next(reader)
headers[0] = "ID"

for row in reader:
    fight = {}
    for i in range(0, len(row) - 1):
        fight[str(headers[i])] = row[i]

    fight["Fighter1"] = fight["Fighter1"].strip()
    fight["Fighter2"] = fight["Fighter2"].strip()

    fight["Status"] = "win" # Three options: win (someone won), draw, nc (no contest)

    if fight["Method"].strip() == "NC":
        fight["Status"] = "nc"
        if fight["Fighter1"][-2:] == "NC":
            fight["Fighter1"] = fight["Fighter1"][:-2] # Remove "NC" from name
        if fight["Fighter2"][-2:] == "NC":
            fight["Fighter2"] = fight["Fighter2"][:-2] # Remove "NC" from name

    elif fight["Fighter2"][-4:] == "loss":
        fight["Fighter1"] = fight["Fighter1"][:-3] # Remove "win" from name
        fight["Fighter2"] = fight["Fighter2"][:-4] # Remove "loss" from name

    elif fight["Fighter2"][-4:] == "draw":
        fight["Fighter1"] = fight["Fighter1"][:-4]  # Remove "draw" from name
        fight["Fighter2"] = fight["Fighter2"][:-4]  # Remove "draw" from name
        fight["Status"] = "draw"

    else:
        if fight["Fighter1"][-2:] == "NC":
            fight["Status"] = "nc"
            fight["Fighter1"] = fight["Fighter1"][:-2] # Remove "NC" from name
        if fight["Fighter2"][-2:] == "NC":
            fight["Status"] = "nc"
            fight["Fighter2"] = fight["Fighter2"][:-2] # Remove "NC" from name

    fights.append(fight)

# Process fighters

f = open('stats/Sherdog_Fighters.csv', newline='')

reader = csv.reader(f, delimiter=',')
headers = next(reader)
headers[0] = "ID"

for row in reader:
    fighters.append(row[1].strip())

# Data validation

if len(fighters) != len(set(fighters)):
    print("Duplicate fighter names")
    exit()

for fight in fights:
    if fight["Fighter1"] not in fighters:
        print("Fighter 1 in fight not in the fighter list: " + fight["Fighter1"])
        exit()
    if fight["Fighter2"] not in fighters:
        print("Fighter 2 in fight not in the fighter list: " + fight["Fighter2"])
        exit()

print("Number of fighters: " + str(len(fighters)))
print("Number of fights: " + str(len(fights)))

# Initialize each fighter's elo to 1200 and number of fights to 0

elo = {}
number_of_fights = {}
for fighter in fighters:
    elo[fighter] = 1000
    number_of_fights[fighter] = 0

def get_k_value(number_of_fights):
    if number_of_fights < 3:
        return 200
    if number_of_fights < 6:
        return 150
    return 100

# Iterate through the fights, calculate elo after each fight

for fight in reversed(fights):
    fighter_1 = fight["Fighter1"]
    fighter_2 = fight["Fighter2"]

    fighter_1_elo = elo[fighter_1]
    fighter_2_elo = elo[fighter_2]

    fight["Fighter1_Before_Elo"] = fighter_1_elo
    fight["Fighter2_Before_Elo"] = fighter_2_elo

    # No contest, no change to elo
    if fight["Status"] == "nc":
        fight["Fighter1_After_Elo"] = fighter_1_elo
        fight["Fighter2_After_Elo"] = fighter_2_elo
        continue

    # Draw or win, recalculate elo
    fighter_1_expected_outcome = 1 / (1 + 10 ** ((fighter_2_elo - fighter_1_elo) / 400))
    fighter_2_expected_outcome = 1 - fighter_1_expected_outcome

    fighter_1_number_of_fights = number_of_fights[fighter_1]
    fighter_2_number_of_fights = number_of_fights[fighter_2]

    fighter_1_k_value = get_k_value(fighter_1_number_of_fights)
    fighter_2_k_value = get_k_value(fighter_2_number_of_fights)

    if fight["Status"] == "win":
        fight["Fighter1_After_Elo"] = fighter_1_elo + fighter_1_k_value * (1 - fighter_1_expected_outcome)
        fight["Fighter2_After_Elo"] = fighter_2_elo + fighter_2_k_value * (0 - fighter_2_expected_outcome)
    else: # fight was a draw
        fight["Fighter1_After_Elo"] = fighter_1_elo + fighter_1_k_value * (0.5 - fighter_1_expected_outcome)
        fight["Fighter2_After_Elo"] = fighter_2_elo + fighter_2_k_value * (0.5 - fighter_2_expected_outcome)

    elo[fighter_1] = fight["Fighter1_After_Elo"]
    elo[fighter_2] = fight["Fighter2_After_Elo"]

    """
    if fight["Fighter1"] == "Conor McGregor":
        print("win: " + str(elo[fighter_1]) + fighter_2)
    if fight["Fighter2"] == "Conor McGregor":
        print("loss: " + str(elo[fighter_2]) + fighter_1)
    """

"""
print(elo["Conor McGregor"])
print(elo["Khabib Nurmagomedov"])

fighter_1_expected_outcome = 1 / (1 + 10 ** ((elo["Khabib Nurmagomedov"] - elo["Conor McGregor"]) / 400))
fighter_2_expected_outcome = 1 - fighter_1_expected_outcome
print(fighter_1_expected_outcome)
print(fighter_2_expected_outcome)
"""

sorted_elo = sorted(elo.items(), key=operator.itemgetter(1), reverse=True)
print(sorted_elo[:20])