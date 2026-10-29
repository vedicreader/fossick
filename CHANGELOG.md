# Release notes

<!-- do not remove -->

## 0.1.23

- `gh_clone` clones over HTTPS only. Before, a failed HTTPS clone tried SSH, and SSH could stop and wait for a passphrase, because `GIT_TERMINAL_PROMPT` does not stop SSH. Pass `ssh=True` to try SSH after HTTPS. SSH then runs with `BatchMode=yes`. An SSH address as the target is cloned over HTTPS too.
- `gh_clone` makes a shallow clone with `depth=1`. Pass `depth=None` for the full history. New `timeout`, 300 seconds by default, applies to each git network command. When git takes longer, fossick stops it, removes the part-made folder and raises `TimeoutError`.
- `gh_clone` gives git its own copy of the environment with `GIT_TERMINAL_PROMPT=0`, and does not change `os.environ`.
- `gh_clone` keeps each clone in a folder named `owner__repo`, with each part percent-encoded and `_` encoded too. Before, `a-b/c` and `a/b-c` used the same `a-b-c` folder. Clones in the old folders are not used again; you can delete them.
- `gh_clone` refuses a target that starts with `-`, and puts `--` before the URL in `git clone`.
- On macOS, the plain HTTP path trusts the system keychain. When no CA variable is set, fossick reads the system keychains with `security find-certificate`, adds the certificates to certifi's roots, and keeps the bundle in its cache folder for one day. On a Mac that inspects TLS, `http_get` and `fetch` then work with no `CURL_CA_BUNDLE`. Verification stays on.

## 0.1.22

- The plain HTTP path of `get_page`, `fetch`, `http_get` and `http_post` connects only to the addresses that `check_url` approved. It gives them to libcurl with `CURLOPT_RESOLVE`, so a second DNS answer cannot send the request to a private address (DNS rebinding). fossick now follows redirects itself. It checks and pins the address of each redirect before it connects, and it does not send cookies, `auth` or credential headers that you supplied to a different host. Through a proxy, and in the browser paths, only the first URL is checked.
- `get_pdf` downloads the PDF again after the NCBI proof-of-work step through the same plain path, with the same checks, timeout and `max_bytes`. Before, this second download used its own curl session with no address check and no redirect check, and any page could start it.
- New `max_bytes` on `fetch`, `get_page`, `http_page` and `get_pdf`: a plain HTTP download that is larger stops with the new `TooLarge` error. New `max_recv_speed` on `fetch` and `get_page` limits the download speed. Both are off by default, so calls that do not set them behave as before. The browser paths ignore them. `http_page` also takes `curl_options`.
- The plain HTTP path, and with it `http_get`, `get_pdf`, its proof-of-work step and `read_arxiv`, takes a CA bundle file for TLS verification. It uses `ca_bundle=` or a path given as `verify=`, else the first file named by `SSL_CERT_FILE`, `CURL_CA_BUNDLE` or `REQUESTS_CA_BUNDLE`, read on each request. This fixes `curl: (60) unable to get local issuer certificate` on a machine that inspects TLS with its own root. The bundle applies only when verification is on, and fossick never turns verification off. With none of these set, nothing changes.
- The plain HTTP path verifies TLS certificates by default. Before, `get_page`, `fetch`, `http_page`, `get_pdf`, `download_files`, `crossref` and `replay_xhr` turned verification off unless you passed `verify=True`. `replay_xhr` sends the debug Chrome's cookies, so it must not send them over an unverified connection. Pass `verify=False` only for a host you trust that has a bad certificate.
- `click_settle` uses `expect_navigation`. fastcdp 0.0.17 removed `wait_ready`, so every click through `click_settle` failed with it. The `fastcdp` floor is now 0.0.17.
- `read_gh_file` passes extra keyword arguments to `http_get`, and `read` passes its own to `read_gh_file`.
- `what_is` and `url2nb` find arXiv and YouTube links by the host of the URL. Before, `https://docs.example.dev/youtube.com-guide` went to the YouTube reader.
- The docs and the docstrings of `fetch` and `read` say that `auto=True` can end in the logged-in debug Chrome on port 9223, with its cookies for the site, and that callers must pass `auto=False` for untrusted URLs. A test proves that with `auto=False` no path starts a browser or connects to the debug Chrome.

## 0.1.21

- `shop_add` with an explicit `variant` picks an exact name match first, then a unique substring match. An ambiguous or unmatched variant, or one that cannot be applied on the page, is refused with `need='variant'` and nothing is added. Before, `variant='L'` could add Small, and a variant on a page without a variant list was ignored.
- A shop operation that passes `Shop.tout` is cancelled, and the `TimeoutError` says the action may already have happened. A `TimeoutError` raised by the operation itself passes through unchanged.
- Short-lived CDP connections and capture tabs are closed when the call ends, also on error.
- `click_settle` starts waiting for the page to settle before it clicks, and ignores only a timeout. The `fastcdp` floor is now 0.0.9, the first release whose page proxy returns `wait_ready` as a context manager.
- `search(page=N)` starts at page N. DuckDuckGo clients are cached per timeout and proxy setting, and image, news and video searches pass `timeout`.
- `focus` stays within its character budget, counting separators and gap markers.
- `snippet_similarity` uses `shingles` and `jaccard`.
- Notebook prose is rewritten in plain technical English.

## 0.1.20
- Chrome, started by `cdp_setup` and `cdp_app`, and the git commands behind `gh_clone` get `/dev/null` as stdin. Neither reads or reconfigures the caller's terminal. `gh_clone` runs git through `subprocess` itself, because fastcore's `run` passes the terminal on.

## 0.1.19
- `debug_ready` is public in `fossick.cdp`: it returns whether the debug Chrome on a port answers at `/json/version`. It starts no Chrome. `_debug_ready` stays as an alias.

## 0.1.18
- `url2nb` and `pdf2nb` work again. `_md2cells` and its helpers, lost in the move to pdflite, are restored.
- `pdf2nb` hands its OCR choice to pdflite as `ocr=`.
- `usable(min_chars=...)` checks that the page has that much readable markdown. `research` passes 0 and measures the markdown it keeps.
- README links `search`, `fetch`, `crawl` and `research` to the library functions, not the CLI.
- CI: the cells that need a live debug Chrome are `eval: false`; the HTTP tests use httpbin.org, as httpbun.com no longer answers; `dev` is an extra, as nbdev's CI installs it, with the uv group pointing at it.

## 0.1.17
pdflite upgrades

## 0.1.16
lean pass

## 0.1.15
fossick single door with read

## 0.1.14
json cache instead of pickle cache

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
    those, non-200s and empty JS shells are now dropped, with the reason in `res['dropped']`. The next hit
    is fetched in their place. `n=5` means five readable sources.
  - `research()` keeps the passages that answer the query instead of each page's first `chars` characters
    (answer-phrase recall 73% → 85% at the default 4000-char budget). `focus()` exposes it; `focused=False`
    restores head truncation.
  - `norm_url()` deduplicates hits that differ only by scheme, `www.`, a trailing slash or tracking params.
  - `search(pages=N)` pulls N result pages from every backend instead of just the first, so a large `n` has
    candidates to return. A simulation produced these approximate pool ceilings:

    | result pages | approximate hits |
    |---|---|
    | 1 | 74 |
    | 2 | 100 |
    | 3 | 110 |

    Ranks run on across pages and a page-2 repeat of a page-1 hit isn't counted twice. `research(pages=N)` and
    `fossick search --pages` expose it. Fan-out no longer depends on `n`. Raising `n` costs no extra requests.
  - Tokenizing for `bm25()` stays a plain `[a-z0-9]+` split. Against sqlite FTS5's `porter` tokenizer — same
    engine, same BM25 params, only the tokenizer differing — stemming *lost* on both jobs: passage recall
    83.5% → 81.9% at a 4000-char budget, hit reranking P@3 0.89 → 0.85. Recorded so it isn't retried blind.

Fixes:

  - Failures loading scrapling's browser fetchers now raise `BrowserUnavailable` naming the cause instead of a
    bare `ValueError` from an import line. `google()` and `fetch(auto=True)` silently swallowed that error.
    "The browser stack is broken" then looked like "Google returned nothing", and bot walls passed as page content.
  - `fetch(auto=True)` records every tier's failure on `page.errs` and warns once when the browser tiers can't load.
  - The ddgs client no longer passes `verify=False`. ddgs maps a bool `verify` to "use the system trust store", so
    behind a TLS-terminating proxy there was no CA to validate against. *Every* backend failed to connect.
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
