# Release notes

<!-- do not remove -->

## 0.1.13
pdf2md layout scrambliing fix

## 0.1.12
lxml readability true

## 0.1.11
increase search quality results

## 0.1.10
bug fix

## 0.1.9
fixes setarr

## 0.1.8
cdp app generationapp 

## 0.1.7
gh clone
## 0.1.6
release


## 0.1.5

Search & research quality:

  - `search()` no longer uses ddgs' aggregation. `DDGS.text()` queries only ~`max_results/10 + 1` randomly
    shuffled backends (so `n=5` asked 2 random engines), merges them by *how many* backends returned a url with
    ranks discarded, then unconditionally hoists every `wikipedia.org` hit to position 1. `search()` now queries
    the backends itself, keeps each one's native ranking, and fuses with reciprocal rank fusion. `fuse=False`
    restores the old path; `backend='google'` restricts to one engine.
  - `rerank()` re-orders hits by relevance to the query — BM25 over title, snippet and url slug by default
    (P@3 0.11 → 0.81 on a 27-page benchmark, ~1ms for 30 hits), or a flashrank cross-encoder with
    `method='flashrank'` (0.85, but 40x slower and a 53MB dependency: `pip install fossick[rerank]`).
  - `research()` counts a source only once it is *readable*. A Cloudflare interstitial is an HTTP 200 that
    converts to "Enable JavaScript and cookies to continue" and used to land in the corpus looking like content;
    those, non-200s and empty JS shells are now dropped — with the reason, in `res['dropped']` — and the next hit
    is fetched in their place, so `n=5` means five readable sources.
  - `research()` keeps the passages that answer the query instead of each page's first `chars` characters
    (answer-phrase recall 73% → 85% at the default 4000-char budget). `focus()` exposes it; `focused=False`
    restores head truncation.
  - `norm_url()` deduplicates hits that differ only by scheme, `www.`, a trailing slash or tracking params.
  - `search(pages=N)` pulls N result pages from every backend instead of just the first, so a large `n` has
    candidates to return — the pool ceiling roughly went 74 → 100 → 110 hits at pages 1 → 2 → 3 in a simulation.
    Ranks run on across pages and a page-2 repeat of a page-1 hit isn't counted twice. `research(pages=N)` and
    `fossick search --pages` expose it. Fan-out no longer depends on `n`, so raising `n` costs no extra requests.
  - Tokenizing for `bm25()` stays a plain `[a-z0-9]+` split. Against sqlite FTS5's `porter` tokenizer — same
    engine, same BM25 params, only the tokenizer differing — stemming *lost* on both jobs: passage recall
    83.5% → 81.9% at a 4000-char budget, hit reranking P@3 0.89 → 0.85. Recorded so it isn't retried blind.

Fixes:

  - Failures loading scrapling's browser fetchers now raise `BrowserUnavailable` naming the cause instead of a
    bare `ValueError` from an import line. `google()` and `fetch(auto=True)` silently swallowed it, which turned
    "the browser stack is broken" into "Google returned nothing" and let bot walls through as page content.
  - `fetch(auto=True)` records every tier's failure on `page.errs` and warns once when the browser tiers can't load.
  - The ddgs client no longer passes `verify=False`. ddgs maps a bool `verify` to "use the system trust store", so
    behind a TLS-terminating proxy there was no CA to validate against and *every* backend failed to connect.
    `ddgs_env()` now reads `HTTPS_PROXY`/`SSL_CERT_FILE` and friends, and backends get a timeout and one retry.
  - One dead host in a `research()` batch no longer aborts the whole batch.

## 0.1.4
gh clone, cach, pull

## 0.1.3
gh md fix

## 0.1.2
github pull without ssh

## 0.1.1
fossick shop and cleanup

## 0.1.0
fixes scrapling bug fix

## 0.0.15

New Features:

  MCP server
  - fossick-mcp — exposes the whole toolkit over the Model Context Protocol, so Claude Code, Claude Desktop, Codex, and any MCP client can drive fossick directly.
  - 23 tools mirroring the Python/CLI API: web_search/research, fetch_page/fetch_pages/crawl_site, the arXiv/YouTube/GitHub/notebook readers, find_hidden_apis/replay_capture/paginate_api, and browse/page_* for the persistent logged-in debug Chrome.
  - stdio by default; fossick-mcp --http for Streamable HTTP. mcp now ships as a core dependency — no extra to install.


## 0.0.14

New Features:

 Smart fetching                                                                                                                              
  - fetch(url, auto=True) — auto-escalates plain → heavy → stealthy → logged-in Chrome, stopping at the first tier that isn't bot-blocked;    
  winning tier on .tier.                                                                                                                      
  - fetch(url, session=True) — routes through the persistent debug Chrome, reusing its logged-in cookies (read authenticated pages with no    
  login code).                                                                                                                                
  - browser_session() — context manager that keeps one browser warm across many fetches (no per-URL relaunch); crawl(..., reuse=True) uses it.
  - Bot-wall detection now covers Cloudflare, Anubis (proof-of-work), and captcha widgets (reCAPTCHA/hCaptcha/Turnstile), matching widgets    
  rather than the bare word.                                                                                                                  
                                                                                                                                              
  Research                                                                                                                                    
  - research(q) — searches, reads the top results in parallel, and returns one cited markdown corpus: {query, sources, digest}.               
                                                                                                                                              
  Hidden APIs                                                                                                                                 
  - find_xhr(url, session=True) — captures a page's XHR calls through the authenticated Chrome; each hit carries a replayable capture.        
  - replay_xhr(capture) — re-issues a captured request as a fast plain-HTTP call using the browser's cookies.                                 
                                                                                                                                              
  Browser/agent toolkit (CDP)                                                                                                                 
  - page.snapshot() — compact [#id] role "name" accessibility view for LLMs.                                                                  
  - page.fill_form({label: value}) / page.act([...]) — fill and drive pages declaratively by label (goto/fill/click/select/read).             
  - node_for / click_sel / fill_sel — bridge CSS selectors to CDP actions; page.html()/selector()/md() pull the live post-JS page into        
  fossick's markdown pipeline.                                                                                                                
  - ax_diff(before, after) — shows what an action changed between two snapshots.                                                              
  - cdp_ws() / cdp_cookies() — expose the debug Chrome's WebSocket URL and cookies for scrapling.                                             
  - Debug Chrome now auto-adds --no-sandbox as root and accepts extra_flags (containers/CI).                                                  
                                                                                                                                              
  CLI                                                                                                                                         
  - New fossick research and fossick ax commands; --session / --auto flags on fossick fetch.                                                  
                                                                                                                                              
  Fixes                                                                                                                                       
  - fossick research CLI no longer errors (_research import); browser_session() works inside notebooks/async loops (async Playwright API).    
    



## 0.0.13
cli fix


## 0.0.12
fastcdp based setup


## 0.0.11
remove searx, use ddgs



## 0.0.10
annotate tout



## 0.0.9
documentation for llm tooling



## 0.0.8
ssl skipping, urm2md idompotency



## 0.0.7
liteparse md fix



## 0.0.6
liteparse for pdf ocr



## 0.0.5
cdp result timeout, pdf2nb fix



## 0.0.4
url2md, collect, annotate



## 0.0.3
pdf2nb, url2nb, searxng start



## 0.0.2
pypi release



## 0.0.1
Initial release of fossick
