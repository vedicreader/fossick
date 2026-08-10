__version__ = "0.1.7"
from .search import *
from .core import *

# `fossick.cdp` drives a real Chrome over the DevTools protocol, and `fossick.shop` builds on it;
# together they cost ~1.3s of fastcdp + playwright + scrapling import. Most callers only ever fetch
# and search, so both are resolved on first touch instead — `fossick.cdp_connect`, `fossick.shop.shop`
# and `from fossick.cdp import *` all still work, they just pay for Chrome when they are used.
# Their names come from nbdev's symbol index, so they cannot drift from what the modules export.
_LAZY_MODS = ('cdp', 'shop')

def _lazy_names():
    "Exported name -> module, for the submodules that are not imported until something asks for them."
    from ._modidx import d
    return {n: f'fossick.{m}' for m in _LAZY_MODS for s in d['syms'][f'fossick.{m}']
            if s.count('.') == 2 and (n := s.rsplit('.', 1)[1]) not in _LAZY_MODS}

def __getattr__(name):
    if name.startswith('_'): raise AttributeError(name)   # never import Chrome to answer a dunder probe
    from importlib import import_module
    if name in _LAZY_MODS: return import_module(f'.{name}', __name__)
    if (mod := _lazy_names().get(name)) is None:
        raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
    return getattr(import_module(mod), name)

def __dir__(): return sorted({*globals(), *_LAZY_MODS, *_lazy_names()})
