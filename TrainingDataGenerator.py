import csv
from datetime import datetime


def process_file(file_name):
    f = open(file_name, newline='')
    reader = csv.reader(f, delimiter=',')
    headers = next(reader)
    all = []
    for row in reader:
        single = {}
        for i in range(0, len(row)):
            single[str(headers[i])] = row[i]
        all.append(single)
    return all

# Fetch raw data

events = process_file('stats/FightMetricEvents.csv')
fights = process_file('stats/FightMetricFightsData.csv')
fighters = process_file('stats/FightMetricFightersData.csv')
elo = process_file('stats/FightsElo.csv')

# Calculate UFC and non-UFC wins, losses, and draws

fight_records = {}

for fighter in fighters:
    id = fighter["id"]

    if len(fighter["url"]) == 0:
        continue # Skip fighters with incomplete data

    fight_record = {
        "total_wins": int(fighter["record_wins"]),
        "total_losses": int(fighter["record_losses"]),
        "total_draws": int(fighter["record_draws"]),
        "ufc_wins": 0,
        "ufc_losses": 0,
        "ufc_draws": 0
    }
    fight_records[id] = fight_record

    # Keep track of stats so far...initialize to 0
    fighter["wins_so_far"] = 0
    fighter["losses_so_far"] = 0
    fighter["draws_so_far"] = 0
    fighter["fight_duration_so_far"] = 0
    fighter["knockdowns_so_far"] = 0
    fighter["sig_strikes_so_far"] = 0
    fighter["sig_strikes_att_so_far"] = 0
    fighter["total_strikes_so_far"] = 0
    fighter["total_strikes_att_so_far"] = 0
    fighter["takedowns_so_far"] = 0
    fighter["takedowns_att_so_far"] = 0
    fighter["submission_att_so_far"] = 0
    #fighter["pass_guard_so_far"] = 0
    fighter["reverse_pos_so_far"] = 0
    fighter["strikes_head_so_far"] = 0
    fighter["strikes_head_att_so_far"] = 0
    fighter["strikes_body_so_far"] = 0
    fighter["strikes_body_att_so_far"] = 0
    fighter["strikes_leg_so_far"] = 0
    fighter["strikes_leg_att_so_far"] = 0
    fighter["strikes_distance_so_far"] = 0
    fighter["strikes_distance_att_so_far"] = 0
    fighter["strikes_clinch_so_far"] = 0
    fighter["strikes_clinch_att_so_far"] = 0
    fighter["strikes_ground_so_far"] = 0
    fighter["strikes_ground_att_so_far"] = 0

for fight in fights:
    fighter1 = fighters[int(fight["fighter1"])]
    fighter2 = fighters[int(fight["fighter2"])]

    fighter1_id = fighter1["id"]
    fighter2_id = fighter2["id"]

    result = fight["result"]
    if result == "W":
        if fighter1_id in fight_records.keys():
            fight_records[fighter1_id]["ufc_wins"] += 1
        if fighter2_id in fight_records.keys():
            fight_records[fighter2_id]["ufc_losses"] += 1
    elif result == "L":
        if fighter1_id in fight_records.keys():
            fight_records[fighter1_id]["ufc_losses"] += 1
        if fighter2_id in fight_records.keys():
            fight_records[fighter2_id]["ufc_wins"] += 1
    elif result == "D":
        if fighter1_id in fight_records.keys():
            fight_records[fighter1_id]["ufc_draws"] += 1
        if fighter2_id in fight_records.keys():
            fight_records[fighter2_id]["ufc_draws"] += 1

for k in fight_records.keys():
    fight_record = fight_records[k]
    fight_record["non_ufc_wins"] = fight_record["total_wins"] - fight_record["ufc_wins"]
    fight_record["non_ufc_losses"] = fight_record["total_losses"] - fight_record["ufc_losses"]
    fight_record["non_ufc_draws"] = fight_record["total_draws"] - fight_record["ufc_draws"]

# Build fight data to feed to the neural net

neural_net_fights = []
debug = False

nn_id = 0
for fight in reversed(fights):
    fighter1 = fighters[int(fight["fighter1"])]
    fighter2 = fighters[int(fight["fighter2"])]

    # Skip training on the fight if either fighter has incomplete data

    fighter1_id = fighter1["id"]
    fighter2_id = fighter2["id"]
    if fighter1_id not in fight_records.keys() or fighter2_id not in fight_records.keys():
        continue;

    # Get result
    result = fight["result"]
    if result == "W":
        nn_result = 1
    elif result == "L":
        nn_result = 0
    elif result == "D":
        nn_result = 0.5
    else:
        continue # Skip no contests

    if debug:
        print("Result: " + str(nn_result))

    # Get elo difference
    fighter1_elo = elo[int(fight["id"])]["fighter1_elo"]
    fighter2_elo = elo[int(fight["id"])]["fighter2_elo"]
    nn_elo = float(fighter1_elo) - float(fighter2_elo)

    if debug:
        print("Elo difference: " + str(nn_elo))

    # Get height difference

    fighter1_height = fighter1["height_inches"]
    fighter2_height = fighter2["height_inches"]
    nn_height = int(fighter1_height) - int(fighter2_height)

    if debug:
        print("Height difference: " + str(nn_height))

    # Get weight difference

    fighter1_weight = fighter1["weight"]
    fighter2_weight = fighter2["weight"]
    nn_weight = int(fighter1_weight) - int(fighter2_weight)

    if debug:
        print("Weight difference: " + str(nn_weight))

    # Get reach difference

    fighter1_reach = fighter1["reach"]
    fighter2_reach = fighter2["reach"]

    if fighter1_reach == "--" or fighter2_reach == "--":
        nn_reach = 0
    else:
        nn_reach = int(fighter1_reach) - int(fighter2_reach)

    if debug:
        print("Reach difference: " + str(nn_reach))

    # Get stance difference

    fighter1_stance = int(fighter1["is_orthodox"])
    fighter2_stance = int(fighter2["is_orthodox"])
    nn_stance = fighter1_stance - fighter2_stance

    if debug:
        print("Stance difference: " + str(nn_stance))

    # Get age difference

    date_format = "%b %d, %Y"
    fighter1_dob = datetime.strptime(fighter1["dob"], date_format)
    fighter2_dob = datetime.strptime(fighter2["dob"], date_format)
    nn_age = int((fighter1_dob - fighter2_dob).days)

    if debug:
        print("Age difference: " + str(nn_age))

    # Get fight record

    fighter1_record = fight_records[fighter1_id]
    fighter2_record = fight_records[fighter2_id]

    fighter1_non_ufc_wins = fighter1_record["non_ufc_wins"]
    fighter2_non_ufc_wins = fighter2_record["non_ufc_wins"]
    nn_non_ufc_wins = fighter1_non_ufc_wins - fighter2_non_ufc_wins

    if debug:
        print("Non-UFC win difference: " + str(nn_non_ufc_wins))

    fighter1_non_ufc_losses = fighter1_record["non_ufc_losses"]
    fighter2_non_ufc_losses = fighter2_record["non_ufc_losses"]
    nn_non_ufc_losses = fighter1_non_ufc_losses - fighter2_non_ufc_losses

    if debug:
        print("Non-UFC loss difference: " + str(nn_non_ufc_losses))

    fighter1_non_ufc_draws = fighter1_record["non_ufc_draws"]
    fighter2_non_ufc_draws = fighter2_record["non_ufc_draws"]
    nn_non_ufc_draws = fighter1_non_ufc_draws - fighter2_non_ufc_draws

    if debug:
        print("Non-UFC draw difference: " + str(nn_non_ufc_draws))

    fighter1_wins_so_far = fighter1["wins_so_far"]
    fighter2_wins_so_far = fighter2["wins_so_far"]
    nn_ufc_wins = fighter1_wins_so_far - fighter2_wins_so_far

    if debug:
        print("UFC win difference: " + str(nn_ufc_wins))

    fighter1_losses_so_far = fighter1["losses_so_far"]
    fighter2_losses_so_far = fighter2["losses_so_far"]
    nn_ufc_losses = fighter1_losses_so_far - fighter2_losses_so_far

    if debug:
        print("UFC loss difference: " + str(nn_ufc_losses))

    fighter1_draws_so_far = fighter1["draws_so_far"]
    fighter2_draws_so_far = fighter2["draws_so_far"]
    nn_ufc_draws = fighter1_draws_so_far - fighter2_draws_so_far

    if debug:
        print("UFC draw difference: " + str(nn_ufc_draws))

    # Get average fight duration difference

    fighter1_fight_duration = fighter1["fight_duration_so_far"] / 60 # Convert minutes to seconds
    fighter2_fight_duration = fighter2["fight_duration_so_far"] / 60 # Convert minutes to seconds
    fighter1_ufc_fight_count = fighter1_wins_so_far + fighter1_losses_so_far + fighter1_draws_so_far
    fighter2_ufc_fight_count = fighter2_wins_so_far + fighter2_losses_so_far + fighter2_draws_so_far

    if fighter1_ufc_fight_count == 0:
        fighter1_average_fight_duration = 0.00001
    else:
        fighter1_average_fight_duration = fighter1_fight_duration / fighter1_ufc_fight_count

    if fighter2_ufc_fight_count == 0:
        fighter2_average_fight_duration = 0.00001
    else:
        fighter2_average_fight_duration = fighter2_fight_duration / fighter2_ufc_fight_count

    nn_fight_duration = (fighter1_average_fight_duration - fighter2_average_fight_duration)

    if debug:
        print("Fight duration difference: " + str(nn_fight_duration))

    # Get average knockdowns per minute difference

    fighter1_knockdowns_per_min = fighter1["knockdowns_so_far"] / fighter1_average_fight_duration
    fighter2_knockdowns_per_min = fighter2["knockdowns_so_far"] / fighter2_average_fight_duration
    nn_knockdowns = fighter1_knockdowns_per_min - fighter2_knockdowns_per_min

    if debug:
        print("Knockdowns/min difference: " + str(nn_knockdowns))

    # Get average sig strikes per minute difference

    fighter1_sig_strikes_per_min = fighter1["sig_strikes_so_far"] / fighter1_average_fight_duration
    fighter2_sig_strikes_per_min = fighter2["sig_strikes_so_far"] / fighter2_average_fight_duration
    nn_sig_strikes = fighter1_sig_strikes_per_min - fighter2_sig_strikes_per_min

    if debug:
        print("Sig strikes/min difference: " + str(nn_sig_strikes))

    # Get average sig strikes attempted per minute difference

    fighter1_sig_strikes_attempted_per_min = fighter1["sig_strikes_att_so_far"] / fighter1_average_fight_duration
    fighter2_sig_strikes_attempted_per_min = fighter2["sig_strikes_att_so_far"] / fighter2_average_fight_duration
    nn_sig_strikes_attempted = fighter1_sig_strikes_attempted_per_min - fighter2_sig_strikes_attempted_per_min

    if debug:
        print("Sig strikes attempted/min difference: " + str(nn_sig_strikes_attempted))

    # Get average total strikes per minute difference

    fighter1_total_strikes_per_min = fighter1["total_strikes_so_far"] / fighter1_average_fight_duration
    fighter2_total_strikes_per_min = fighter2["total_strikes_so_far"] / fighter2_average_fight_duration
    nn_total_strikes = fighter1_total_strikes_per_min - fighter2_total_strikes_per_min

    if debug:
        print("Total strikes/min difference: " + str(nn_total_strikes))

    # Get average total strikes attempted per minute difference

    fighter1_total_strikes_attempted_per_min = fighter1["total_strikes_att_so_far"] / fighter1_average_fight_duration
    fighter2_total_strikes_attempted_per_min = fighter2["total_strikes_att_so_far"] / fighter2_average_fight_duration
    nn_total_strikes_attempted = fighter1_total_strikes_attempted_per_min - fighter2_total_strikes_attempted_per_min

    if debug:
        print("Total strikes attempted/min difference: " + str(nn_total_strikes_attempted))

    # Get average takedowns per minute difference

    fighter1_takedowns_per_min = fighter1["takedowns_so_far"] / fighter1_average_fight_duration
    fighter2_takedowns_per_min = fighter2["takedowns_so_far"] / fighter2_average_fight_duration
    nn_takedowns = fighter1_takedowns_per_min - fighter2_takedowns_per_min

    if debug:
        print("Takedowns/min difference: " + str(nn_takedowns))

    # Get average takedowns attempted per minute difference

    fighter1_takedowns_attempted_per_min = fighter1["takedowns_att_so_far"] / fighter1_average_fight_duration
    fighter2_takedowns_attempted_per_min = fighter2["takedowns_att_so_far"] / fighter2_average_fight_duration
    nn_takedowns_attempted = fighter1_takedowns_attempted_per_min - fighter2_takedowns_attempted_per_min

    if debug:
        print("Takedowns attempted/min difference: " + str(nn_takedowns_attempted))

    # Get average submissions attempted per minute difference

    fighter1_submissions_attempted_per_min = fighter1["submission_att_so_far"] / fighter1_average_fight_duration
    fighter2_submissions_attempted_per_min = fighter2["submission_att_so_far"] / fighter2_average_fight_duration
    nn_submissions_attempted = fighter1_submissions_attempted_per_min - fighter2_submissions_attempted_per_min

    if debug:
        print("Submissions attempted/min difference: " + str(nn_submissions_attempted))

    # Get average position reversals per minute difference

    fighter1_rev_per_min = fighter1["reverse_pos_so_far"] / fighter1_average_fight_duration
    fighter2_rev_per_min = fighter2["reverse_pos_so_far"] / fighter2_average_fight_duration
    nn_rev = fighter1_rev_per_min - fighter2_rev_per_min

    if debug:
        print("Reversals/min difference: " + str(nn_rev))

    # Get average head strikes per minute difference

    fighter1_strikes_head_per_min = fighter1["strikes_head_so_far"] / fighter1_average_fight_duration
    fighter2_strikes_head_per_min = fighter2["strikes_head_so_far"] / fighter2_average_fight_duration
    nn_strikes_head = fighter1_strikes_head_per_min - fighter2_strikes_head_per_min

    if debug:
        print("Head strikes/min difference: " + str(nn_strikes_head))

    # Get average head strikes attempted per minute difference

    fighter1_strikes_head_attempted_per_min = fighter1["strikes_head_att_so_far"] / fighter1_average_fight_duration
    fighter2_strikes_head_attempted_per_min = fighter2["strikes_head_att_so_far"] / fighter2_average_fight_duration
    nn_strikes_head_attempted = fighter1_strikes_head_attempted_per_min - fighter2_strikes_head_attempted_per_min

    if debug:
        print("Head strikes attempted/min difference: " + str(nn_strikes_head_attempted))

    # Get average body strikes per minute difference

    fighter1_strikes_body_per_min = fighter1["strikes_body_so_far"] / fighter1_average_fight_duration
    fighter2_strikes_body_per_min = fighter2["strikes_body_so_far"] / fighter2_average_fight_duration
    nn_strikes_body = fighter1_strikes_body_per_min - fighter2_strikes_body_per_min

    if debug:
        print("Body strikes/min difference: " + str(nn_strikes_body))

    # Get average body strikes attempted per minute difference

    fighter1_strikes_body_attempted_per_min = fighter1["strikes_body_att_so_far"] / fighter1_average_fight_duration
    fighter2_strikes_body_attempted_per_min = fighter2["strikes_body_att_so_far"] / fighter2_average_fight_duration
    nn_strikes_body_attempted = fighter1_strikes_body_attempted_per_min - fighter2_strikes_body_attempted_per_min

    if debug:
        print("Body strikes attempted/min difference: " + str(nn_strikes_body_attempted))

    # Get average leg strikes per minute difference

    fighter1_strikes_leg_per_min = fighter1["strikes_leg_so_far"] / fighter1_average_fight_duration
    fighter2_strikes_leg_per_min = fighter2["strikes_leg_so_far"] / fighter2_average_fight_duration
    nn_strikes_leg = fighter1_strikes_leg_per_min - fighter2_strikes_leg_per_min

    if debug:
        print("Leg strikes/min difference: " + str(nn_strikes_leg))

    # Get average leg strikes attempted per minute difference

    fighter1_strikes_leg_attempted_per_min = fighter1["strikes_leg_att_so_far"] / fighter1_average_fight_duration
    fighter2_strikes_leg_attempted_per_min = fighter2["strikes_leg_att_so_far"] / fighter2_average_fight_duration
    nn_strikes_leg_attempted = fighter1_strikes_leg_attempted_per_min - fighter2_strikes_leg_attempted_per_min

    if debug:
        print("Leg strikes attempted/min difference: " + str(nn_strikes_leg_attempted))

    # Get average distance strikes per minute difference

    fighter1_strikes_distance_per_min = fighter1["strikes_distance_so_far"] / fighter1_average_fight_duration
    fighter2_strikes_distance_per_min = fighter2["strikes_distance_so_far"] / fighter2_average_fight_duration
    nn_strikes_distance = fighter1_strikes_distance_per_min - fighter2_strikes_distance_per_min

    if debug:
        print("Distance strikes/min difference: " + str(nn_strikes_distance))

    # Get average distance strikes attempted per minute difference

    fighter1_strikes_distance_attempted_per_min = fighter1["strikes_distance_att_so_far"] / fighter1_average_fight_duration
    fighter2_strikes_distance_attempted_per_min = fighter2["strikes_distance_att_so_far"] / fighter2_average_fight_duration
    nn_strikes_distance_attempted = fighter1_strikes_distance_attempted_per_min - fighter2_strikes_distance_attempted_per_min

    if debug:
        print("Distance strikes attempted/min difference: " + str(nn_strikes_distance_attempted))

    # Get average clinch strikes per minute difference

    fighter1_strikes_clinch_per_min = fighter1["strikes_clinch_so_far"] / fighter1_average_fight_duration
    fighter2_strikes_clinch_per_min = fighter2["strikes_clinch_so_far"] / fighter2_average_fight_duration
    nn_strikes_clinch = fighter1_strikes_clinch_per_min - fighter2_strikes_clinch_per_min

    if debug:
        print("Clinch strikes/min difference: " + str(nn_strikes_clinch))

    # Get average clinch strikes attempted per minute difference

    fighter1_strikes_clinch_attempted_per_min = fighter1["strikes_clinch_att_so_far"] / fighter1_average_fight_duration
    fighter2_strikes_clinch_attempted_per_min = fighter2["strikes_clinch_att_so_far"] / fighter2_average_fight_duration
    nn_strikes_clinch_attempted = fighter1_strikes_clinch_attempted_per_min - fighter2_strikes_clinch_attempted_per_min

    if debug:
        print("Clinch strikes attempted/min difference: " + str(nn_strikes_clinch_attempted))

    # Get average ground strikes per minute difference

    fighter1_strikes_ground_per_min = fighter1["strikes_ground_so_far"] / fighter1_average_fight_duration
    fighter2_strikes_ground_per_min = fighter2["strikes_ground_so_far"] / fighter2_average_fight_duration
    nn_strikes_ground = fighter1_strikes_ground_per_min - fighter2_strikes_ground_per_min

    if debug:
        print("Ground strikes/min difference: " + str(nn_strikes_ground))

    # Get average ground strikes attempted per minute difference

    fighter1_strikes_ground_attempted_per_min = fighter1["strikes_ground_att_so_far"] / fighter1_average_fight_duration
    fighter2_strikes_ground_attempted_per_min = fighter2["strikes_ground_att_so_far"] / fighter2_average_fight_duration
    nn_strikes_ground_attempted = fighter1_strikes_ground_attempted_per_min - fighter2_strikes_ground_attempted_per_min

    if debug:
        print("Ground strikes attempted/min difference: " + str(nn_strikes_ground_attempted))

    # Build dictionary

    nn_fight = {
        "id": nn_id,
        "result": nn_result,
        "elo": nn_elo,
        "height_inches": nn_height,
        "weight_lbs": nn_weight,
        "reach_inches": nn_reach,
        "is_orthodox": nn_stance,
        "age_days": nn_age,
        "non_ufc_wins": nn_non_ufc_wins,
        "non_ufc_losses": nn_non_ufc_losses,
        "non_ufc_draws": nn_non_ufc_draws,
        "ufc_wins": nn_ufc_wins,
        "ufc_losses": nn_ufc_losses,
        "ufc_draws": nn_ufc_draws,

        "avg_fight_duration_mins": nn_fight_duration,
        "avg_knockdowns_per_min": nn_knockdowns,
        "avg_sig_strikes_per_min": nn_sig_strikes,
        "avg_sig_strikes_att_per_min": nn_sig_strikes_attempted,
        "avg_takedowns_per_min": nn_takedowns,
        "avg_takedowns_att_per_min": nn_takedowns_attempted,
        "avg_submission_att_per_min": nn_submissions_attempted

    }
    """
        "avg_fight_duration_mins": nn_fight_duration,
        "avg_knockdowns_per_min": nn_knockdowns,
        "avg_sig_strikes_per_min": nn_sig_strikes,
        "avg_sig_strikes_att_per_min": nn_sig_strikes_attempted,
        "avg_total_strikes_per_min": nn_total_strikes,
        "avg_total_strikes_att_per_min": nn_total_strikes_attempted,
        "avg_takedowns_per_min": nn_takedowns,
        "avg_takedowns_att_per_min": nn_takedowns_attempted,
        "avg_submission_att_per_min": nn_submissions_attempted,
        #"avg_pass_guard_per_min":,
        "avg_reverse_pos_per_min": nn_rev,
        "avg_sig_strikes_head_per_min": nn_strikes_head,
        "avg_sig_strikes_head_att_per_min": nn_strikes_head_attempted,
        "avg_sig_strikes_body_per_min": nn_strikes_body,
        "avg_sig_strikes_body_att_per_min": nn_strikes_body_attempted,
        "avg_sig_strikes_leg_per_min": nn_strikes_leg,
        "avg_sig_strikes_leg_att_per_min": nn_strikes_leg_attempted,
        "avg_sig_strikes_distance_per_min": nn_strikes_distance,
        "avg_sig_strikes_distance_att_per_min": nn_strikes_distance_attempted,
        "avg_sig_strikes_clinch_per_min": nn_strikes_clinch,
        "avg_sig_strikes_clinch_att_per_min": nn_strikes_clinch_attempted,
        "avg_sig_strikes_ground_per_min": nn_strikes_ground,
        "avg_sig_strikes_ground_att_per_min": nn_strikes_ground_attempted
    """

    neural_net_fights.append(nn_fight)

    # Update stats for next fight

    # Update record

    if result == "W":
        fighter1["wins_so_far"] += 1
        fighter2["losses_so_far"] += 1
    elif result == "L":
        fighter1["losses_so_far"] += 1
        fighter2["wins_so_far"] += 1
    elif result == "D":
        fighter1["draws_so_far"] += 1
        fighter2["draws_so_far"] += 1

    # Update fight duration in seconds (assume 5 minutes, or 300 seconds per round)

    num_rounds = (int(fight["round"]) - 1)
    last_round_time = fight["time"].split(":")
    last_round_minutes = int(last_round_time[0])
    last_round_seconds = int(last_round_time[1])
    fight_duration = 300 * num_rounds + 60 * last_round_minutes + last_round_seconds
    fighter1["fight_duration_so_far"] += fight_duration
    fighter2["fight_duration_so_far"] += fight_duration

    # Update fight statistics

    fighter1["knockdowns_so_far"] += int(fight["fighter1_knockdowns"])
    fighter2["knockdowns_so_far"] += int(fight["fighter2_knockdowns"])

    fighter1["sig_strikes_so_far"] += int(fight["fighter1_sig_strikes"])
    fighter2["sig_strikes_so_far"] += int(fight["fighter2_sig_strikes"])

    fighter1["sig_strikes_att_so_far"] += int(fight["fighter1_sig_strikes_attempt"])
    fighter2["sig_strikes_att_so_far"] += int(fight["fighter2_sig_strikes_attempt"])

    fighter1["total_strikes_so_far"] += int(fight["fighter1_total_strikes"])
    fighter2["total_strikes_so_far"] += int(fight["fighter2_total_strikes"])

    fighter1["total_strikes_att_so_far"] += int(fight["fighter1_total_strikes_attempt"])
    fighter2["total_strikes_att_so_far"] += int(fight["fighter2_total_strikes_attempt"])

    fighter1["takedowns_so_far"] += int(fight["fighter1_takedowns"])
    fighter2["takedowns_so_far"] += int(fight["fighter2_takedowns"])

    fighter1["takedowns_att_so_far"] += int(fight["fighter1_takedowns_attempt"])
    fighter2["takedowns_att_so_far"] += int(fight["fighter2_takedowns_attempt"])

    fighter1["submission_att_so_far"] += int(fight["fighter1_submission_attempts"])
    fighter2["submission_att_so_far"] += int(fight["fighter2_submission_attempts"])

    #fighter1["pass_guard_so_far"] += int(fight["fighter1_pass"])
    #fighter2["pass_guard_so_far"] += int(fight["fighter2_pass"])

    fighter1["reverse_pos_so_far"] += int(fight["fighter1_rev"])
    fighter2["reverse_pos_so_far"] += int(fight["fighter2_rev"])

    fighter1["strikes_head_so_far"] += int(fight["fighter1_sig_strikes_head"])
    fighter2["strikes_head_so_far"] += int(fight["fighter2_sig_strikes_head"])

    fighter1["strikes_head_att_so_far"] += int(fight["fighter1_sig_strikes_head_attempt"])
    fighter2["strikes_head_att_so_far"] += int(fight["fighter2_sig_strikes_head_attempt"])

    fighter1["strikes_body_so_far"] += int(fight["fighter1_sig_strikes_body"])
    fighter2["strikes_body_so_far"] += int(fight["fighter2_sig_strikes_body"])

    fighter1["strikes_body_att_so_far"] += int(fight["fighter1_sig_strikes_body_attempt"])
    fighter2["strikes_body_att_so_far"] += int(fight["fighter2_sig_strikes_body_attempt"])

    fighter1["strikes_leg_so_far"] += int(fight["fighter1_sig_strikes_leg"])
    fighter2["strikes_leg_so_far"] += int(fight["fighter2_sig_strikes_leg"])

    fighter1["strikes_leg_att_so_far"] += int(fight["fighter1_sig_strikes_leg_attempt"])
    fighter2["strikes_leg_att_so_far"] += int(fight["fighter2_sig_strikes_leg_attempt"])

    fighter1["strikes_distance_so_far"] += int(fight["fighter1_sig_strikes_distance"])
    fighter2["strikes_distance_so_far"] += int(fight["fighter2_sig_strikes_distance"])

    fighter1["strikes_distance_att_so_far"] += int(fight["fighter1_sig_strikes_distance_attempt"])
    fighter2["strikes_distance_att_so_far"] += int(fight["fighter2_sig_strikes_distance_attempt"])

    fighter1["strikes_clinch_so_far"] += int(fight["fighter1_sig_strikes_clinch"])
    fighter2["strikes_clinch_so_far"] += int(fight["fighter2_sig_strikes_clinch"])

    fighter1["strikes_clinch_att_so_far"] += int(fight["fighter1_sig_strikes_clinch_attempt"])
    fighter2["strikes_clinch_att_so_far"] += int(fight["fighter2_sig_strikes_clinch_attempt"])

    fighter1["strikes_ground_so_far"] += int(fight["fighter1_sig_strikes_ground"])
    fighter2["strikes_ground_so_far"] += int(fight["fighter2_sig_strikes_ground"])

    fighter1["strikes_ground_att_so_far"] += int(fight["fighter1_sig_strikes_ground_attempt"])
    fighter2["strikes_ground_att_so_far"] += int(fight["fighter2_sig_strikes_ground_attempt"])

    nn_id += 1

def write_csv_file(file_name, dict):
    file = open(file_name, 'w', newline="")
    keys = dict[0].keys()
    writer = csv.DictWriter(file, keys)
    writer.writeheader()
    writer.writerows(dict)

write_csv_file('stats/NeuralNetworkData.csv', neural_net_fights)