import csv
import math

def analyse_parameter_testings(cvs_path):
    best_parameters = []
    best_guess = math.inf
    best_wr = 0

    with open(cvs_path, "r", newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            avg_g = float(row["Average Guess"])
            win_ratio = float(row["Win Ratio"])
            params = row["Parameters"]

            if win_ratio > best_wr:  # Getting greatest win ration
                best_parameters.clear()
                best_parameters.append(params)
                best_wr = win_ratio
                best_guess = avg_g
            elif win_ratio == best_wr:
                if avg_g < best_guess:  # Getting lowers guess rate
                    best_parameters.clear()
                    best_parameters.append(params)
                    best_guess = avg_g
                elif avg_g == best_wr:
                    best_parameters.append(params)

    print("Average Guess:", best_guess, "\t\tWin rate:", best_wr, "\t\tParameters", best_parameters)

analyse_parameter_testings("parameter_tweaking/tree500.csv")