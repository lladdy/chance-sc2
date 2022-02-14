from decider import Decider

dec = Decider()
dec.decide('build', ['FourRax', "FiveRax"])
dec.register_result(True, save_to_file=False)
