#!/usr/bin/env python3
"""Golden-source evaluation for fossick's retrieval quality.

Schema and contract tests answer "is the output shaped right". This answers the question they
cannot see: **is the right source in the result set, and is it near the top?** For a question about
Australian building rules that means the state planning portal above the lead-generation
marketplaces; for a Stack Overflow question it means the original above the scrapers.

Two modes, and the split is the point:

    python evals/golden.py                  # replay: offline, deterministic, no network, CI-safe
    python evals/golden.py --record         # live: hit the real backends, write a review draft

**Replay runs the real code over pinned inputs.** A fixture stores the raw hits a backend returned,
not a finished answer, and replay pushes them through `infer_region`, `classify` and `curate` as they
exist today. So the fixture is an input, not a recording of an output: improve the ranking and the
eval gets *better* rather than stale. (This is where it diverges from the harness it is modelled on,
which replays a finished payload and can only detect regressions away from what was recorded.)

**Recording is a draft, not a result.** `--record` writes `<fixture>.recorded.json` and refuses to
touch the canonical file, because expectations derived from what a search engine happened to return
today are a description of today, not a standard. `floor_expectations` says so in its name: it emits
the weakest assertions that would pass, and the workflow is

    1. record   python evals/golden.py --record
    2. review   open fixtures/golden.recorded.json and *tighten* every `expect` block by hand --
                name the primary source that should win, the domains that should never appear
    3. promote  move it to fixtures/golden.json

Step 2 is the whole exercise. A gold standard is a human judgement about what a good answer looks
like; anything else just freezes the status quo and calls it a benchmark.
"""
from __future__ import annotations

import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from fossick.quality import classify, curate, diversity, host, plan, registrable_domain
except Exception:
    # `import fossick` pulls the browser stack in through `fossick.search`. `quality` itself is
    # stdlib-only, so load it directly and let a checkout without scrapling still score a ranking.
    import importlib.util
    _spec = importlib.util.spec_from_file_location(
        'fossick_quality', Path(__file__).resolve().parents[1] / 'fossick' / 'quality.py')
    _q = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_q)
    classify, curate, diversity, plan = _q.classify, _q.curate, _q.diversity, _q.plan
    host, registrable_domain = _q.host, _q.registrable_domain

# `infer_region` does live in `fossick.search`, so the region check is the one thing that needs the
# full install. A missing check is reported in the output, never skipped silently.
try:
    from fossick.search import infer_region
except Exception as e:                                    # pragma: no cover - environment-dependent
    infer_region, _REGION_ERR = None, f'{type(e).__name__}: {e}'

FIXTURES = Path(__file__).parent / 'fixtures' / 'golden.json'
BODY_CHARS = 300           # keep recorded fixtures reviewable by a person
CHECKS = ('region', 'intent', 'top_domain_any_of', 'must_include_domains', 'blocked_domains',
          'required_terms', 'min_results', 'min_domains', 'max_domain_share', 'max_dup_urls', 'min_near_dups', 'plan_min', 'plan_covers', 'min_sources', 'max_sources')


def validate(fx: dict) -> list:
    "Contract violations in one fixture, so a hand-edited file fails loudly rather than passing vacuously."
    bad = []
    for k in ('id', 'query', 'hits', 'expect'):
        if k not in fx: bad.append(f'missing {k!r}')
    for i, h in enumerate(fx.get('hits') or []):
        if not isinstance(h, dict) or not (h.get('href') or h.get('url')):
            bad.append(f'hits[{i}] has no href')
    for k in fx.get('expect') or {}:
        if k not in CHECKS: bad.append(f'unknown expectation {k!r} (known: {", ".join(CHECKS)})')
    if not (fx.get('expect') or {}): bad.append('empty expect block — a fixture with no claim tests nothing')
    return bad


def evaluate(fx: dict) -> dict:
    "Run one fixture through the live curation code and report which expectations failed."
    q, exp = fx['query'], fx.get('expect') or {}
    hits, rep = curate(q, [dict(h) for h in fx['hits']])
    doms = [registrable_domain(h.get('href') or h.get('url', '')) for h in hits]
    doms = [d for d in doms if d]
    hosts = [host(h.get('href') or h.get('url', '')) for h in hits]
    text = ' '.join(str(h.get(k) or '') for h in hits for k in ('title', 'body', 'content')).lower()
    div = rep['diversity']
    fail, skip = [], []

    def named(want, got):                # an expectation may name a host or a registrable domain
        return any(g == want or g.endswith(f'.{want}') for g in got)

    if (want := exp.get('region')) is not None:
        if infer_region is None: skip.append(f'region ({_REGION_ERR})')
        elif (got := infer_region(q)) != want: fail.append(f'region: want {want}, got {got}')
    sub = plan(q)
    if (m := exp.get('plan_min')) is not None and len(sub) < m:
        fail.append(f'plan: want >={m} searches, got {len(sub)} ({sub})')
    for term in exp.get('plan_covers') or []:
        if not any(term.lower() in s.lower() for s in sub[1:]):
            fail.append(f'plan covers nothing about {term!r}: {sub[1:]}')
    if 'intent' in exp and (got := classify(q)) != exp['intent']:
        fail.append(f'intent: want {exp["intent"]}, got {got}')
    if (any_of := exp.get('top_domain_any_of')) and not any(named(w, hosts[:1] + doms[:1]) for w in any_of):
        fail.append(f'top source: want one of {any_of}, got {hosts[0] if hosts else "(none)"}')
    for w in exp.get('must_include_domains') or []:
        if not named(w, hosts + doms): fail.append(f'missing required source {w}')
    for w in exp.get('blocked_domains') or []:
        if named(w, hosts + doms): fail.append(f'blocked source present: {w}')
    for t in exp.get('required_terms') or []:
        if t.lower() not in text: fail.append(f'missing term {t!r}')
    if (m := exp.get('min_results')) is not None and len(hits) < m:
        fail.append(f'results: want >={m}, got {len(hits)}')
    if (m := exp.get('min_domains')) is not None and div['domains'] < m:
        fail.append(f'domains: want >={m}, got {div["domains"]}')
    if (m := exp.get('max_domain_share')) is not None:
        share = (div['dominant_domain'] or {}).get('share', 0)
        if share > m: fail.append(f'one domain holds {share:.0%} of the page, max {m:.0%}')
    if (m := exp.get('max_dup_urls')) is not None and div['dup_urls'] > m:
        fail.append(f'duplicate urls: want <={m}, got {div["dup_urls"]}')
    if (m := exp.get('min_near_dups')) is not None and div['near_dups'] < m:
        fail.append(f'near-duplicate pairs: want >={m}, got {div["near_dups"]} (syndication undetected)')
    if (m := exp.get('min_sources')) is not None and div['sources'] < m:
        fail.append(f'independent sources: want >={m}, got {div["sources"]}')
    if (m := exp.get('max_sources')) is not None and div['sources'] > m:
        fail.append(f'independent sources: want <={m}, got {div["sources"]} (syndication not clustered)')

    return dict(id=fx['id'], category=fx.get('category'), query=q,
                status='fail' if fail else 'ok', failures=fail, skipped=skip,
                intent=rep['intent'], plan=sub, top=hosts[0] if hosts else None,
                order=hosts, dropped=rep['dropped'], demoted=rep['demoted'],
                diversity=div)


def floor_expectations(q: str, hits: list) -> dict:
    "The weakest expectations that would pass today. A starting point for review, never a standard."
    doms = {registrable_domain(h.get('href') or h.get('url', '')) for h in hits}
    doms.discard('')
    out = dict(min_results=max(1, min(len(hits), 3)), min_domains=max(1, min(len(doms), 3)),
               max_dup_urls=0)
    if infer_region is not None: out['region'] = infer_region(q)
    if (c := classify(q)) is not None: out['intent'] = c
    return out


def record(queries: list, n: int) -> tuple:
    "Run the live backends and build review drafts. Returns (fixtures, errors)."
    from fossick.search import search
    out, errs = [], []
    for case in queries:
        try: hits = search(case['query'], n=n)
        except Exception as e:
            errs.append(dict(id=case['id'], error=f'{type(e).__name__}: {e}')); continue
        if not hits:
            errs.append(dict(id=case['id'], error='no results')); continue
        clean = [dict(title=str(h.get('title') or ''), href=str(h.get('href') or h.get('url') or ''),
                      body=str(h.get('body') or h.get('content') or '')[:BODY_CHARS])
                 for h in hits]
        out.append(dict(id=case['id'], category=case.get('category'), query=case['query'],
                        notes=case.get('notes', ''), hits=clean,
                        expect=floor_expectations(case['query'], clean),
                        REVIEW='Tighten this expect block by hand before promoting. Name the source '
                               'that SHOULD win and the domains that should never appear.'))
    return out, errs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('--fixtures', type=Path, default=FIXTURES)
    p.add_argument('--record', action='store_true', help='hit the live backends and write a review draft')
    p.add_argument('-n', type=int, default=10, help='hits to record per query')
    p.add_argument('-v', '--verbose', action='store_true', help='print the ranking for every case')
    a = p.parse_args()

    cases = json.loads(a.fixtures.read_text(encoding='utf-8'))

    if a.record:
        dest = a.fixtures.with_suffix('.recorded.json')
        if dest.resolve() == a.fixtures.resolve():
            print('refusing to overwrite the canonical fixture', file=sys.stderr); return 2
        fx, errs = record(cases, a.n)
        dest.write_text(json.dumps(fx, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(dict(recorded=len(fx), errors=errs, out=str(dest)), indent=2))
        print(f'\nNow review {dest} and tighten every expect block before promoting it.', file=sys.stderr)
        return 1 if errs else 0

    broken = [(fx.get('id', f'#{i}'), b) for i, fx in enumerate(cases) if (b := validate(fx))]
    if broken:
        for i, b in broken: print(f'INVALID {i}: {"; ".join(b)}', file=sys.stderr)
        return 2

    rows = [evaluate(fx) for fx in cases]
    for r in rows:
        mark = 'ok  ' if r['status'] == 'ok' else 'FAIL'
        print(f'{mark} {r["id"]:<28} intent={str(r["intent"]):<10} top={r["top"]}')
        for s in r['skipped']: print(f'       skipped check: {s}')
        for f in r['failures']: print(f'       {f}')
        if a.verbose:
            if len(r['plan']) > 1: print(f'       plan:  {" | ".join(r["plan"][1:])}')
            print(f'       order: {" > ".join(r["order"])}')
            print(f'       dropped={r["dropped"]} demoted={r["demoted"]} '
                  f'urls={r["diversity"]["n"]} sources={r["diversity"]["sources"]} '
                  f'diversity={r["diversity"]["score"]}')
    bad = [r for r in rows if r['status'] != 'ok']
    skipped = sum(len(r['skipped']) for r in rows)
    print(f'\n{len(rows)-len(bad)}/{len(rows)} pass' + (f' ({skipped} checks skipped)' if skipped else ''))
    return 1 if bad else 0


if __name__ == '__main__':
    raise SystemExit(main())
