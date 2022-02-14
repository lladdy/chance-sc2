from decider import Decider

dec = Decider(file='test.json')
dec.decide('build', ['FourRax', "FiveRax"])
dec.register_result(True)
