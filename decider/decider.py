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

scalar = 0.1
samples = np.array([55, 10])
wins = np.array([50, 10])
win_perc = wins/samples

initial_prob = (expit(samples*scalar)-0.5)*2
prob_inverse = 1-initial_prob
adjusted_probs = win_perc+prob_inverse
prob_sum = np.sum(adjusted_probs)
scaled_probs = adjusted_probs/prob_sum
prob_check_sum = np.sum(scaled_probs)

print(f'Samples: {samples}')
print(f'Wins: {wins}')
print(f'Win %: {win_perc}')
print(f'Initial Prob: {initial_prob}')
print(f'Prob Inv: {prob_inverse}')
print(f'Actual Prob: {adjusted_probs}')
print(f'Prob Sum: {prob_sum}')
print(f'Scaled Prob: {scaled_probs}')
print(f'Prob Sum: {prob_check_sum}')



# num_choices = 2
# one_hundred_over_all_choices = 1.0/num_choices
# print(one_hundred_over_all_choices)
# win_percentage = 1.0  # starts at 0.0
# num_samples = 1
#
# samples_prob = (expit(num_samples)-0.5)*2
# print(samples_prob)
# shaped_probability = win_percentage*samples_prob
# print(shaped_probability)
# actual_probability = (one_hundred_over_all_choices-samples_prob)
# print(actual_probability)

