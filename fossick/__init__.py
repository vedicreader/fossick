__version__ = "0.1.28"
from .search import *
from .core import *
from .quality import *

# `fossick.cdp` controls Chrome through the DevTools protocol. `fossick.shop` uses `fossick.cdp`.
# Their imports (fastcdp, playwright and scrapling) take about 1.3 s. Most callers only fetch and search.
# These two modules load when a caller first uses a name from them, not at `import fossick`.
# `fossick.cdp_connect`, `fossick.shop.shop` and `from fossick.cdp import *` work as before.
# The list of their names comes from nbdev's symbol index. It always matches what the modules export.
_LAZY_MODS = ('cdp', 'shop')

def _lazy_names():
    "Map each exported name of the lazy modules to the name of its module."
    from ._modidx import d
    return {n: f'fossick.{m}' for m in _LAZY_MODS for s in d['syms'][f'fossick.{m}']
            if s.count('.') == 2 and (n := s.rsplit('.', 1)[1]) not in _LAZY_MODS}

def __getattr__(name):
    if name.startswith('_'): raise AttributeError(name)   # a check for a private or dunder name never loads the Chrome modules
    from importlib import import_module
    if name in _LAZY_MODS: return import_module(f'.{name}', __name__)
    if (mod := _lazy_names().get(name)) is None:
        raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
    return getattr(import_module(mod), name)

def __dir__(): return sorted({*globals(), *_LAZY_MODS, *_lazy_names()})
