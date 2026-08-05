__version__ = "0.1.0"
from .search import *
from .core import *

# `fossick.cdp` drives a real Chrome over the DevTools protocol, and importing it costs ~0.13s of
# fastcdp + playwright. Most callers only ever fetch and search, so it is resolved on first use
# rather than at import. Names stay reachable exactly as before — `fossick.cdp_connect`,
# `from fossick import *`, `from fossick.cdp import syncy` — the cost just moves to first touch.
_CDP_NAMES = ('cdp_setup', 'cdp_connect', 'cdp_ws', 'cdp_cookies', 'ax_diff',
              'BUTTON_JS', 'HIDE', 'SHOW', 'ANNOTATE_JS', 'ANNOTATE_BAR_JS', 'ANNOTATE_CLEANUP_JS')
# `fossick.shop` is deferred for the same reason: it builds on `fossick.cdp`, so importing it eagerly
# would pay the Chrome-stack import cost for every caller who only wants `fetch`.
_SHOP_NAMES = ('shop', 'Shop', 'ShopError', 'SHOP_JS', 'SITES', 'site_hint', 'FIELD_MAP', 'match_fields')
_LAZY = {**{n: '.cdp' for n in _CDP_NAMES}, **{n: '.shop' for n in _SHOP_NAMES}}

def __getattr__(name):
    if name not in _LAZY: raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
    from importlib import import_module
    return getattr(import_module(_LAZY[name], __name__), name)

def __dir__(): return sorted({*globals(), *_LAZY})
