#!/usr/bin/env python3
"""Which parts of `fossick.cdp` a given browser engine actually supports.

`engine='obscura'` and `obscura_connect()` swap the browser behind the DevTools protocol, and the
protocol is not the contract: a server can answer `Accessibility.getFullAXTree` and still return a
tree with no accessible names in it, which turns `snapshot()` into a list of `[#24] textbox ""` and
`fill_form()` into a lookup that matches nothing. CDP has no capability handshake, and unimplemented
methods come back as an empty result rather than an error, so the only way to know is to drive the
real helpers against the real engine and look at what came back.

That is what this does. It serves a fixture page with the shapes that separate engines — a
`display:none` decoy carrying the same label as a real field, a `<select>`, a click that reveals
content, a page that builds itself from `fetch()` — and runs the checks against every endpoint you
point it at:

    python evals/cdp_engines.py                    # obscura (started on demand) vs Chrome, if present
    python evals/cdp_engines.py --port 9223        # whatever is already listening there
    python evals/cdp_engines.py --engine obscura   # just the one

A check that fails is not a bug report: it is the map of which half of the module to use on that
engine. Anything addressed by CSS survives an engine swap; anything addressed by accessible name is
where they diverge. `nbs/01_cdp.ipynb` carries the summary table, and this is what regenerates it.
"""
import argparse, asyncio, functools, http.server, os, shutil, socket, sys, tempfile, threading, time

# The fixture is on loopback, which `check_url` and obscura both refuse by default. Say so before
# importing fossick: `obscura_ws` reads this when it decides how to launch the server.
os.environ.setdefault('FOSSICK_ALLOW_PRIVATE', '1')

FIXTURE = '''<!doctype html><html><head><meta charset="utf-8"><title>CDP probe</title>
<style>.gone{display:none}</style></head><body>
<h1>Probe</h1><p id="para">Hello from the probe page.</p>
<form class="gone"><label>Email <input name="email_decoy" type="text"></label></form>
<form id="real" onsubmit="event.preventDefault();document.getElementById('out').textContent=
  'submitted:'+document.querySelector('#real [name=email]').value">
  <label>Email <input name="email" type="text"></label>
  <label>Plan <select name="plan"><option value="free">Free</option><option value="pro">Pro</option></select></label>
  <button type="submit" name="go">Sign up</button>
</form>
<div id="out"></div>
<a href="#target" id="lnk">A link</a>
<button id="reveal" onclick="document.getElementById('later').className=''">Reveal</button>
<div id="later" class="gone">revealed content</div>
<script>window.__probe = 41 + 1;</script>
</body></html>'''

def free_port():
    "A port nothing is listening on. `cdp_connect` reuses whatever answers on its default, and a stray\n    obscura on 9223 will happily answer as `chrome` and make the two columns agree for the wrong reason."
    with socket.socket() as s: s.bind(('127.0.0.1', 0)); return s.getsockname()[1]

def serve_fixture():
    "Serve `FIXTURE` on a free loopback port, and return its URL."
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            body = FIXTURE.encode()
            self.send_response(200); self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', str(len(body))); self.end_headers()
            self.wfile.write(body)
        def log_message(self, *a): pass
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', free_port()), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f'http://127.0.0.1:{srv.server_address[1]}/'

# Each check is (name, async fn -> anything, predicate). The predicate holds the claim; keeping it
# separate from the call is what lets "answered, but with nothing in it" read as a failure.
def checks(url):
    async def _eval_stmt(pg):
        "A statement, not an expression: `Runtime.evaluate` is specified to take either."
        await pg.eval('var __x = 1; __x + 1')
        return True
    async def _hidden_decoy(pg):
        "Chrome drops `display:none` from the AX tree. An engine that does not will match the decoy."
        snap = await pg.snapshot()
        return sum(1 for l in snap.splitlines() if 'textbox' in l or 'searchbox' in l)
    async def _fill(pg):
        bid = await pg.node_for('#real [name=email]')
        await pg.type_text(bid, 'a@b.com')
        return await pg.eval('document.querySelector("#real [name=email]").value')
    async def _click(pg):
        await pg.click_sel('#reveal', wait=False)
        await asyncio.sleep(.5)
        return await pg.eval('getComputedStyle(document.getElementById("later")).display')
    async def _select(pg):
        await pg.select_option(await pg.node_for('#real [name=plan]'), 'pro')
        return await pg.eval('document.querySelector("#real [name=plan]").value')
    async def _form(pg):
        await pg.goto(url)
        await pg.fill_form({'Email': 'z@y.com'}, submit='Sign up')
        await asyncio.sleep(.5)
        return await pg.eval('document.getElementById("out").textContent')
    _CONTROLS = ('textbox', 'searchbox', 'combobox', 'button', 'link')
    async def _named_ax(pg):
        """Accessible names on the *controls* — what `snapshot`, `act` and `fill_form` address.

        Counting the whole tree hides the failure: static text carries a name on every engine, so a
        tree where only the controls come back nameless still looks well populated."""
        tree = await pg.ax_tree()
        if not tree: return 0
        return sum(1 for r in _CONTROLS for n in tree.find_all(role=r) if (n.name or '').strip())
    async def _ancestors(pg):
        await pg.accessibility.enable()
        r = await pg.accessibility.getAXNodeAndAncestors(backendNodeId=await pg.node_for('#lnk'))
        return len((r.get('nodes') or []) if isinstance(r, dict) else (r or []))
    async def _newdoc(pg):
        await pg.page.addScriptToEvaluateOnNewDocument(source='window.__injected=99')
        await pg.goto(url)
        return await pg.eval('window.__injected')
    async def _binding(pg, cdp):
        await pg.runtime.enable()
        await pg.runtime.addBinding(name='__probe_bind')
        async with cdp.on('Runtime.bindingCalled') as q:
            await pg.eval('window.__probe_bind && window.__probe_bind("hi")')
            try: return bool(await asyncio.wait_for(q.get(), 4))
            except asyncio.TimeoutError: return False
    async def _resbody(pg, cdp):
        await pg.network.enable()
        async with cdp.on('Network.responseReceived') as q:
            await pg.goto(url)
            try: m = await asyncio.wait_for(q.get(), 6)
            except asyncio.TimeoutError: return ''
        b = await pg.network.getResponseBody(requestId=m['params']['requestId'])
        return (b or {}).get('body', '')
    return [
        ('eval expression',      lambda pg, c: pg.eval('window.__probe'),        lambda r: r == 42),
        ('eval statement',       lambda pg, c: _eval_stmt(pg),                   lambda r: r is True),
        ('eval object',          lambda pg, c: pg.eval('({a:1,b:[2,3]})'),       lambda r: r == {'a': 1, 'b': [2, 3]}),
        ('eval awaits promise',  lambda pg, c: pg.eval('Promise.resolve(7)'),    lambda r: r == 7),
        ('html',                 lambda pg, c: pg.html(),                        lambda r: '<h1>Probe' in (r or '')),
        ('md',                   lambda pg, c: pg.md(),                          lambda r: 'Probe' in (r or '')),
        ('screenshot',           lambda pg, c: pg.screenshot(),                  lambda r: bool(getattr(r, 'data', None))),
        ('node_for (CSS)',       lambda pg, c: pg.node_for('#lnk'),              lambda r: isinstance(r, int) and r > 0),
        ('DOM.getBoxModel',      lambda pg, c: _boxmodel(pg),                     lambda r: bool(r)),
        ('click',                lambda pg, c: _click(pg),                       lambda r: r == 'block'),
        ('select_option',        lambda pg, c: _select(pg),                      lambda r: r == 'pro'),
        ('type_text',            lambda pg, c: _fill(pg),                        lambda r: r == 'a@b.com'),
        ('fill_form by label',   lambda pg, c: _form(pg),                        lambda r: r == 'submitted:z@y.com'),
        ('ax names on controls', lambda pg, c: _named_ax(pg),                    lambda r: r >= 5),
        ('ax_tree hides hidden', lambda pg, c: _hidden_decoy(pg),                lambda r: r == 1),
        ('getAXNodeAndAncestors',lambda pg, c: _ancestors(pg),                   lambda r: r > 0),
        ('wait_for_selector',    lambda pg, c: pg.wait_for_selector('#para', timeout=5), lambda r: bool(r)),
        ('wait_for_text',        lambda pg, c: pg.wait_for_text('Hello from the probe', timeout=5), lambda r: bool(r)),
        ('addScriptOnNewDoc',    lambda pg, c: _newdoc(pg),                      lambda r: r == 99),
        ('Runtime.addBinding',   lambda pg, c: _binding(pg, c),                  lambda r: r is True),
        ('getResponseBody',      lambda pg, c: _resbody(pg, c),                  lambda r: '<' in (r or '')),
    ]

async def _boxmodel(pg):
    return (await pg.DOM.getBoxModel(backendNodeId=await pg.node_for('#reveal'))).get('content')

async def probe(name, connect, url, timeout=20, close=False):
    "Run every check against one engine. Returns {check: (ok, detail)}."
    from fossick.cdp import snapshot  # noqa: F401 -- registers the @patch helpers on CDP
    out = {}
    cdp = await connect()
    pg = await cdp.new_page()
    await pg.goto(url)
    for cname, call, ok in checks(url):
        try:
            r = await asyncio.wait_for(call(pg, cdp), timeout)
            out[cname] = (bool(ok(r)), str(r)[:60])
        except asyncio.TimeoutError: out[cname] = (False, f'timeout after {timeout}s')
        except Exception as e: out[cname] = (False, f'{type(e).__name__}: {str(e)[:60]}')
        await pg.goto(url)  # each check starts from a clean page
    # Both engines here are this run's own, on ports it chose; leaving one behind means the next run
    # silently probes a stale server instead of a fresh one. Bounded, because obscura 0.2.1 never
    # answers `Browser.close` and an unbounded wait would hang the eval rather than end it.
    if close:
        try: await asyncio.wait_for(cdp.browser.close(), 3)
        except Exception:
            print(f'{name}: Browser.close went unanswered; a server may still be listening',
                  file=sys.stderr)
    return out

def engines(only=None, port=None):
    "The endpoints to probe: an explicit `port`, else obscura and Chrome when each is available."
    from fossick.cdp import cdp_connect, obscura_connect
    if port: return [(f'port {port}', functools.partial(cdp_connect, port=port))]
    out = []
    if only in (None, 'obscura') and (shutil.which('obscura') or os.getenv('FOSSICK_OBSCURA')):
        # Its own port, not OBSCURA_PORT: `obscura_ws` reuses a live server as-is, and one started
        # earlier for ordinary fetching has no --allow-private-network and cannot see the fixture.
        out.append(('obscura', functools.partial(obscura_connect, port=free_port())))
    if only in (None, 'chrome'):
        try:
            from fastcdp import chrome_bin; chrome_bin()
            # Its own port and its own profile: a second Chrome on a shared `user_data_dir` hands off
            # to the first and exits, and the port it was asked for never opens.
            out.append(('chrome', functools.partial(cdp_connect, port=free_port(), headless=True,
                                                    user_data_dir=tempfile.mkdtemp(prefix='fossick-eval-'))))
        except Exception as e: print(f'skipping chrome: {e}', file=sys.stderr)
    return out

async def main(args):
    url = serve_fixture()
    eng = engines(args.engine, args.port)
    if not eng: return print('no engine to probe: install obscura or Chrome, or pass --port', file=sys.stderr) or 1
    res = {}
    for name, connect in eng:
        t = time.time()
        res[name] = await probe(name, connect, url, close=True)
        print(f'{name}: {sum(o for o, _ in res[name].values())}/{len(res[name])} in {time.time()-t:.1f}s',
              file=sys.stderr)
    names = list(res)
    w = max(len(c) for c in res[names[0]])
    print(f'\n{"check".ljust(w)}  ' + '  '.join(n.center(9) for n in names))
    print('-' * (w + 2 + 11 * len(names)))
    for c in res[names[0]]:
        print(f'{c.ljust(w)}  ' + '  '.join(('   ok    ' if res[n][c][0] else '  FAIL   ').center(9) for n in names))
    for n in names:
        bad = {c: d for c, (o, d) in res[n].items() if not o}
        if bad:
            print(f'\n{n} failures:')
            for c, d in bad.items(): print(f'  {c}: {d}')
    return 0

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--engine', choices=('obscura', 'chrome'), help='probe only this engine')
    p.add_argument('--port', type=int, help='probe whatever CDP server is already on this port')
    sys.exit(asyncio.run(main(p.parse_args())))
