import importlib
import pkgutil
from thor2timesketch import mappers


def load_all_mappers() -> None:
    for _, module_name, _ in pkgutil.iter_modules(mappers.__path__):
        importlib.import_module(f"{mappers.__name__}.{module_name}")
