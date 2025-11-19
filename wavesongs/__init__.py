"""
A Python package for generating synthetic bird songs through
physical modeling and numerical optimization techniques.
"""

import pkgutil
import importlib

package = __package__
for loader, module_name, is_pkg in pkgutil.iter_modules(__path__):
    module = importlib.import_module(f".{module_name}", package)
    for attr in getattr(module, "__all__", []):
        globals()[attr] = getattr(module, attr)

from warnings import filterwarnings
filterwarnings('ignore')