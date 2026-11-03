# Decisions

This page lists the decisions that a maintainer must know. Each entry gives the decision, the reason, the version, and the place in the code.
This repo has no CLAUDE.md. The house style and the rules of the package family are in Leela's CLAUDE.md. The changes of each release are in the [CHANGELOG](../CHANGELOG.md). Old design notes are in `docs/superpowers/`, which is not in git.

## What lives here, what does not

- **fossick fetches, searches, clones and drives Chrome.** Web search, page fetch and crawl, HTML to markdown, the arXiv, GitHub, YouTube and PDF readers, CDP, the CLI and the MCP server are here. Apps and shalya call fossick for these. They do not keep their own copies. `fossick/core.py`, `cdp.py`, `search.py`.
- **fossick does not depend on the code index or memory packages.** It sits low in the package graph, with litesearch. koshas, vishalakshi and shalya sit above it. Do not add them, also not to the dev extra: a dev dependency on a package that needs fossick is a cycle. (28 Aug 2026) `pyproject.toml`.
- **The PDF work is pdflite.** fossick only calls it. (28 Aug 2026) `from pdflite import` in `nbs/00_core.ipynb`.
- **The browser is fastcdp.** fossick adds snapshots, forms, steps and network capture on top. `nbs/01_cdp.ipynb`.

## One door

- **`read(target)` is the one door to every reader.** `what_is` picks the reader. A path that exists on disk wins over each URL rule. URLs match by host, not by text. Each reader gives the same seven fields. (24 Aug 2026, 0.1.22) `read`, `what_is` in `nbs/00_core.ipynb`.
- **`read` does not raise for a known target that gives nothing.** It gives `ok=False` and a reason in `skipped`. It raises `ValueError` only for a target of no known kind. `read`.
- **A folder or a repository is not made into text.** `read` gives its local path in `meta['path']`, and the caller picks the files. `read`.

## Safety of the network

- **`auto=True` can end in the logged-in Chrome.** The debug Chrome runs on port 9223 with the profile `~/.cache/fastcdp/cdp-chrome` and has the cookies of the user. For a URL that comes from a page, a document or another person, callers pass `auto=False`. A test proves that `auto=False` starts no browser. (0.1.22) `fetch`, `read`, `cdp_connect`.
- **The plain HTTP path pins the checked address.** `check_url` refuses private and local addresses. libcurl gets the checked address with `CURLOPT_RESOLVE`, and fossick follows each redirect itself and checks it, so DNS rebinding cannot reach `127.0.0.1`. Credentials do not go to a different host. (0.1.22) `check_url`, `_checked_http`.
- **TLS verification is on, always.** fossick never turns it off. A CA bundle comes from `ca_bundle=`, `SSL_CERT_FILE`, `CURL_CA_BUNDLE` or `REQUESTS_CA_BUNDLE`. On macOS, with none set, it adds the system keychain to certifi's roots, so a Mac that inspects TLS works. (0.1.22, 0.1.23) `_verify`, `_system_ca`.
- **`gh_clone` is HTTPS, shallow and has a timeout.** SSH can wait for a passphrase, so it is opt-in with `BatchMode=yes`. git gets its own environment with `GIT_TERMINAL_PROMPT=0`. (0.1.23) `gh_clone`.
- **Chrome and git get `/dev/null` as stdin.** They must not read or change the terminal of the caller. (0.1.20) `cdp_setup`, `_git`.

## Caches and optional parts

- **Caches store JSON, not pickle.** A pickle from the cache can run code. (24 Aug 2026) the JSON `diskcache.Index` in `nbs/00_core.ipynb`.
- **Memory in `fetch` and `search` is off by default.** `cache=`, `per_host=` and `remember_blocks=` turn it on. `forget()` clears it. (0.1.25) `fetch`, `forget`.
- **flashrank is a lazy import, not an extra.** `method='flashrank'` raises `ImportError` with the fix when it is not installed. (27 Aug 2026) `flashrank_scores` in `nbs/02_search.ipynb`.

## Release and docs

- **The README comes from `nbs/index.ipynb`.** Do not edit README.md by hand. (28 Aug 2026)
- **Cells that need a live Chrome do not run in CI.** They have `eval: false`. HTTP tests use httpbin.org. (19 Oct 2026)
- **The skill file ships in the package.** `fossick/SKILL.md` lists the helpers for agents. Add each new public helper to it. (1 Nov 2026)
