# Release notes

<!-- do not remove -->

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


