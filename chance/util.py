import inspect
import sys


def get_strats_from_module(module: str) -> list:
    return inspect.getmembers(sys.modules[module], inspect.isclass)
