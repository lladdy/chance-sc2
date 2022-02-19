from typing import List

from decider import Decider


def test_standard_usage():
    dec = Decider()
    dec.decide('build', ['FourRax', "FiveRax"])
    dec.register_result(True, save_to_file=False)


def ladder_crash_scenario(filename: str, scopes: str, options: List[str], result: bool = True,
                          save_to_file: bool = False):
    dec = Decider(file=filename)
    dec.decide(scopes, options)
    dec.register_result(result, save_to_file=save_to_file)


def ladder_crash_scenario_1():
    ladder_crash_scenario("test/ladder_crash_scenario_1.json",
                          "build",
                          ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"])


def omit_missing_historial_options():
    ladder_crash_scenario("test/omit_missing_historial_options.json",
                          "build",
                          ["2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"])


test_standard_usage()
ladder_crash_scenario_1()
omit_missing_historial_options()
