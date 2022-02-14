import json

import numpy as np
from scipy.special import expit



class Decider:
    # Store:
    # Number of times decision_name was made
    # Number of times option was chosen.
    # Number of times option ended with win.

    def __init__(self, load_file='./data/decider.json'):
        self.decisions: dict = {}
        with open(load_file) as f:
            self.decisions: dict = json.load(f)
            # todo: sanity check wins aren't more than times chosen

    def decide(self, decision_name, options) -> str:
        """
        Makes a decision between choices, taking into account match history.
        """
        # Retrieve percentage win for each option from
        p = None
        if decision_name in self.decisions:
            chosen_count: list = []
            won_count: list = []
            for decision in self.decisions:
                won_count.append(decision['won_count'])
                chosen_count.append(decision['chosen_count'])

            p = self._calc_choice_probabilities(np.array(chosen_count), np.array(won_count))
        else:
            self.decisions[decision_name] = {}

        choice = np.random.choice(options, p=p)
        self.decisions[choice]['chosen_count'] += 1
        return choice

    def report_win_loss(self, win: bool):
        """
        Registers the outcome of the current match.
        """

    @staticmethod
    def _calc_choice_probabilities(chosen_count: np.array, won_count: np.array) -> np.array:
        """
        Determines the weighted probabilities for each choice.
        """
        scalar = 0.1
        win_perc = np.divide(won_count, chosen_count, out=np.zeros_like(won_count, dtype=float), where=chosen_count != 0)

        # calculate a weight that will make low sample size choices more likely
        probability_weight = 1 - (expit(chosen_count * scalar) - 0.5) * 2

        # Apply that weight to each choice's win percentage
        weighted_probabilities = win_perc + probability_weight

        # Scale probabilities back down so they sum to 1.0 again.
        prob_sum = np.sum(weighted_probabilities)
        scaled_probs = weighted_probabilities / prob_sum

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


dec = Decider()
dec.decide()
