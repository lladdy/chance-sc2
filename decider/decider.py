import json

from scipy.special import expit

import numpy as np

import math



class Decider:
    # Store:
    # Number of times decision_name was made
    # Number of times option was chosen.
    # Number of times option ended with win.

    def __init__(self, load_file='./data/decider.json'):
        with open(load_file) as f:
            self.decision_information = json.load(f)

    def decide(self, decision_name, options):
        pass
        # Retrieve percentage win for each option from

# for x in range(1, 100):
#     numpy.random.choice(2, p=[0.1, 0.2])

# Games played: 10
# FourRax = 9 choices 9 Wins
# FiveRax =  1 choices  1 Wins


def calc_choice_probabilities(samples: np.array, wins: np.array) -> np.array:
    scalar = 0.1
    win_perc = wins/samples

    # calculate a weight that will make low sample size choices more likely
    probability_weight = 1-(expit(samples*scalar)-0.5)*2

    # Apply that weight to each choice's win percentage
    weighted_probabilities = win_perc+probability_weight

    # Scale probabilities back down so they sum to 1.0 again.
    prob_sum = np.sum(weighted_probabilities)
    scaled_probs = weighted_probabilities/prob_sum

    # Sanity check in case of bug
    prob_check_sum = np.sum(scaled_probs)
    assert prob_check_sum == 1.0, f'Is there a bug? prob_check_sum was {prob_check_sum}'

    # print(f'Samples: {samples}')
    # print(f'Wins: {wins}')
    # print(f'Win %: {win_perc}')
    # print(f'Prob Inv: {probability_weight}')
    # print(f'Actual Prob: {weighted_probabilities}')
    # print(f'Prob Sum: {prob_sum}')
    # print(f'Scaled Prob: {scaled_probs}')
    # print(f'Prob Sum: {prob_check_sum}')
    return scaled_probs


calc_choice_probabilities(np.array([55, 10]), np.array([50, 10]))

