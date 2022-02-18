import json
import os

import numpy as np
from scipy.special import expit


def floor(array: np.array, precision=0):
    # https://stackoverflow.com/questions/58065055/floor-and-ceil-with-number-of-decimals
    return np.true_divide(np.floor(array * 10 ** precision), 10 ** precision)


def fix_p(p):
    if p.sum() != 1.0:
        p = p * (1. / p.sum())
    return p


class Decider:
    # Store:
    # Number of times decision_name was made
    # Number of times option was chosen.
    # Number of times option ended with win.

    def __init__(self, file='./data/decision_cache.json', create_file_on_missing=True, rounding_precision: int = 4):
        self.global_decision_history: dict = {}
        self.match_decision_history: dict = {}
        self.file = file
        self.rounding_precision = rounding_precision

        if create_file_on_missing and not os.path.isfile(file):
            with open(file, 'w') as f:
                json.dump(self.global_decision_history, f)

        with open(file) as f:
            self.global_decision_history: dict = json.load(f)
            # todo: sanity check wins aren't more than times chosen

    def decide(self, decision_name, options) -> (str, float):
        """
        Makes a decision between choices, taking into account match history.

        TODO: allow for decision scopes where the caller can register things like their opponent/race/etc in the decision
        TODO: have decisions with a similar (but not the same) set of scopes influence other decisions.
        TODO: e.g.
        TODO: BUG - Don't consider historical options that aren't listed
        """
        # Retrieve percentage win for each option from
        chosen_count: list = []
        won_count: list = []
        if decision_name in self.global_decision_history:

            # Intialize missing values
            for option in options:
                if option not in self.global_decision_history[decision_name]:
                    self.global_decision_history[decision_name][option] = {'chosen_count': 0, 'won_count': 0}

            # Prepare data for call to probabilities calc
            for _, decision in self.global_decision_history[decision_name].items():
                won_count.append(decision['won_count'])
                chosen_count.append(decision['chosen_count'])

        else:
            # Intialize missing values
            self.global_decision_history[decision_name] = {}
            for option in options:
                self.global_decision_history[decision_name][option] = {'chosen_count': 0, 'won_count': 0}
                won_count.append(0)
                chosen_count.append(0)

        p = self._calc_choice_probabilities(np.array(chosen_count), np.array(won_count))
        choice = np.random.choice(options, p=fix_p(p))

        if choice not in self.global_decision_history[decision_name]:
            self.global_decision_history[decision_name][choice] = {'chosen_count': 0, 'won_count': 0}

        self.global_decision_history[decision_name][choice]['chosen_count'] += 1
        self._record_match_decision(decision_name, choice)
        return choice, p[options.index(choice)]

    def _record_match_decision(self, decision_name, choice_made):
        if decision_name not in self.match_decision_history:
            self.match_decision_history[decision_name] = []

        if choice_made not in self.match_decision_history[decision_name]:
            self.match_decision_history[decision_name].append(choice_made)

    def register_result(self, win: bool, save_to_file=True):
        """
        Registers the outcome of the current match.
        """

        # todo: register win against decisions made
        if win:
            for decision_name in self.match_decision_history:
                for choice_made in self.match_decision_history[decision_name]:
                    self.global_decision_history[decision_name][choice_made]['won_count'] += 1

        if save_to_file:
            self._save_state_to_file()

    def _save_state_to_file(self, file_override: str = None):
        """
        Saves the current state of the decider to file.
        """

        file_to_use = self.file
        if file_override is not None:
            file_to_use = file_override

        with open(file_to_use, 'w') as f:
            json.dump(self.global_decision_history, f)

    def _calc_choice_probabilities(self, chosen_count: np.array, won_count: np.array) -> np.array:
        """
        Determines the weighted probabilities for each choice.
        """
        scalar = 0.1
        win_perc = np.divide(won_count, chosen_count, out=np.zeros_like(won_count, dtype=float),
                             where=chosen_count != 0)

        # calculate a weight that will make low sample size choices more likely
        probability_weight = 1 - (expit(chosen_count * scalar) - 0.5) * 2

        # Apply that weight to each choice's win percentage
        weighted_probabilities = win_perc + probability_weight

        # Scale probabilities back down so they sum to 1.0 again.
        prob_sum = np.sum(weighted_probabilities)
        scaled_probs = weighted_probabilities / prob_sum

        # Avoid rounding errors by taking the rounding error difference
        # scaled_probs = scaled_probs / scaled_probs.sum(axis=0, keepdims=1)
        scaled_probs = self._round_probabilities_sum(scaled_probs)

        # Sanity check in case of bug
        prob_check_sum = np.sum(scaled_probs)
        # assert prob_check_sum == 1.0, f'Is there a bug? prob_check_sum was {prob_check_sum}'

        # print(f'Samples: {samples}')
        # print(f'Wins: {wins}')
        print(f'Win %: {win_perc}')
        print(f'Prob Inv: {probability_weight}')
        print(f'Actual Prob: {weighted_probabilities}')
        print(f'Prob Sum: {prob_sum}')
        print(f'Scaled Prob: {scaled_probs}')
        print(f'Prob Check Sum: {prob_check_sum}')
        assert prob_check_sum == 1.0, f'Is there a bug? prob_check_sum was {prob_check_sum}'

        return scaled_probs

    def _round_probabilities_sum(self, probabilities: np.array) -> np.array:
        probabilities = floor(probabilities, self.rounding_precision)
        round_amount = 1.0 - np.sum(probabilities)
        probabilities[0] += round_amount  # chuck it on the first one
        return probabilities
