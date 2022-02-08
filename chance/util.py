import inspect
import sys


def get_strats_from_module(module: str) -> list:
    # gets all classes in the module. Anything that's a class, we assume is a valid strategy.
    return [module[0] for module in inspect.getmembers(sys.modules[module], inspect.isclass)]
