

# fossick

Drop-in for `WebSearch` and `WebFetch`. Always prefer fossick.

``` python
from fossick import *
from fossick.search import search, searxng_start
from fossick.cdp import cdp_connect, syncy
```

Run `searxng_start()` once per session before `search()`.

------------------------------------------------------------------------

## Decision tree

    Need web info?
    ├── arxiv URL or ID          -> read_arxiv(url_or_id)
    ├── YouTube URL              -> read_yt(url)
    ├── Download YouTube media   -> download_yt(url, format='audio'|'video')
    ├── Search YouTube           -> search_yt(q, n=10)
    ├── GitHub file URL          -> read_gh_file(url)
    ├── GitHub repo              -> read_gh_repo(url, globs=('README*', '*.py'))
    ├── Search query (no URL)    -> search(q, n=10)
    ├── URL/arxiv/PDF -> notebook -> url2nb(url) or pdf2nb(url_or_path)
    └── Have a URL?
        ├── static page          -> fetch(url) + to_md(page, sel='...')
        ├── JS-rendered          -> fetch(url, heavy=True)
        ├── bot-protected        -> fetch(url, stealthy=True)
        ├── multiple pages/links -> crawl(url, follow_sel='a[href]', max_pages=N)
        ├── multiple known URLs  -> fetch_all(urls)
        ├── hidden JSON API      -> find_xhr(url, pattern='*api*') -> paginate_api(...)
        ├── intercept requests   -> cdp.calls(url, pattern='*api*')
        ├── screenshot           -> pg.collect(save_dir='.', count=1)
        ├── annotate for LLM     -> pg.annotate(save_dir='.')
        └── interactive/SSO      -> cdp_connect() + pg.ax_tree() + fill_text/click_and_wait

------------------------------------------------------------------------

## API

<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr>
<th>Function</th>
<th>Purpose</th>
<th>Key params</th>
<th>Returns</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>searxng_start()</code></td>
<td>Start SearXNG</td>
<td>—</td>
<td>str (URL)</td>
</tr>
<tr>
<td><code>search(q)</code></td>
<td>Web search</td>
<td><code>n</code>, <code>category</code>, <code>engines</code></td>
<td><code>L[Result]</code></td>
</tr>
<tr>
<td><code>lookup_doi(title)</code></td>
<td>DOI for paper title</td>
<td>—</td>
<td>str|None</td>
</tr>
<tr>
<td><code>fetch(url)</code></td>
<td>Fetch a URL</td>
<td><code>sel</code>, <code>heavy</code>, <code>stealthy</code>,
<code>cache</code></td>
<td>Page dict</td>
</tr>
<tr>
<td><code>to_md(page, sel)</code></td>
<td>HTML -&gt; markdown</td>
<td><code>sel</code>, <code>multi</code>, <code>wrap_tag</code></td>
<td>str</td>
</tr>
<tr>
<td><code>crawl(url)</code></td>
<td>Follow links</td>
<td><code>follow_sel</code>, <code>same_domain</code>,
<code>max_pages</code></td>
<td>list[Page]</td>
</tr>
<tr>
<td><code>fetch_all(urls)</code></td>
<td>Parallel fetch</td>
<td><code>sel</code>, <code>concurrency</code></td>
<td>list[Page]</td>
</tr>
<tr>
<td><code>find_xhr(url)</code></td>
<td>Capture hidden API calls</td>
<td><code>pattern</code>, <code>json_only</code></td>
<td>list[dict]</td>
</tr>
<tr>
<td><code>paginate_api(url)</code></td>
<td>Paginate JSON API</td>
<td><code>payload</code>, <code>page_field</code>,
<code>max_pages</code></td>
<td>list</td>
</tr>
<tr>
<td><code>url2nb(url)</code></td>
<td>URL/arxiv/PDF -&gt; notebook</td>
<td><code>nb_path</code></td>
<td>Path</td>
</tr>
<tr>
<td><code>pdf2nb(url_or_path)</code></td>
<td>PDF -&gt; notebook</td>
<td><code>nb_path</code>, <code>image_dir</code></td>
<td>Path</td>
</tr>
<tr>
<td><code>read_arxiv(url)</code></td>
<td>Paper metadata + full text</td>
<td><code>save_pdf</code>, <code>force</code></td>
<td>dict</td>
</tr>
<tr>
<td><code>read_yt(url)</code></td>
<td>YouTube metadata + transcript</td>
<td><code>force</code></td>
<td>dict</td>
</tr>
<tr>
<td><code>search_yt(q)</code></td>
<td>YouTube search</td>
<td><code>n</code></td>
<td><code>L[dict]</code></td>
</tr>
<tr>
<td><code>read_gh_repo(url)</code></td>
<td>Read repo files</td>
<td><code>globs</code>, <code>limit</code>, <code>as_list</code></td>
<td>dict|list</td>
</tr>
<tr>
<td><code>read_gh_file(url)</code></td>
<td>Read one GitHub file</td>
<td>—</td>
<td>str</td>
</tr>
<tr>
<td><code>cdp_connect(port)</code></td>
<td>Connect to Chrome DevTools</td>
<td><code>port</code></td>
<td>CDP</td>
</tr>
<tr>
<td><code>syncy(coro)</code></td>
<td>Run async coroutine sync</td>
<td>—</td>
<td>any</td>
</tr>
<tr>
<td><code>cdp.open_page(url)</code></td>
<td>Open new tab</td>
<td>—</td>
<td>Page</td>
</tr>
<tr>
<td><code>cdp.calls(url, pattern)</code></td>
<td>Capture network requests</td>
<td><code>tail</code></td>
<td>dict</td>
</tr>
<tr>
<td><code>pg.ax_tree()</code></td>
<td>Accessibility tree with node IDs</td>
<td>—</td>
<td>AXTree</td>
</tr>
<tr>
<td><code>pg.fill_text(id, text)</code></td>
<td>Fill form field by node ID</td>
<td>—</td>
<td>—</td>
</tr>
<tr>
<td><code>pg.click_and_wait(id)</code></td>
<td>Click and wait for navigation</td>
<td>—</td>
<td>—</td>
</tr>
<tr>
<td><code>pg.collect(save_dir)</code></td>
<td>Screenshot capture</td>
<td><code>count</code>, <code>tout</code>, <code>every_n</code></td>
<td>list</td>
</tr>
<tr>
<td><code>pg.annotate(save_dir)</code></td>
<td>Label elements; returns screenshot + AX data</td>
<td>—</td>
<td>(img, list)</td>
</tr>
<tr>
<td><code>download_yt(url)</code></td>
<td>Download YouTube audio/video</td>
<td><code>format</code>, <code>save_dir</code></td>
<td>Path</td>
</tr>
</tbody>
</table>

------------------------------------------------------------------------

## Patterns

### JS-rendered / bot-protected

``` python
page = fetch('https://example.com/spa', heavy=True)
page = fetch('https://example.com', stealthy=True)
text = to_md(page, sel='main')  # always use sel= to strip nav/ads
```

### arxiv

``` python
paper = read_arxiv('2306.14881')
text = paper['source'][:8000]  # papers are 30-100k chars; always slice
```

### Notebooks

``` python
nb = url2nb('https://arxiv.org/abs/2306.14881')
nb = pdf2nb('report.pdf')
nb = pdf2nb('https://example.com/paper.pdf', 'notes.ipynb')
```

### Screenshots

``` python
cdp   = syncy(cdp_connect())
pg    = syncy(cdp.open_page('https://example.com'))
shots = syncy(pg.collect(save_dir='shots', count=1))              # single
shots = syncy(pg.collect(save_dir='shots', every_n=5, tout=30))   # auto every 5s
```

### Set-of-Marks annotation

``` python
img, elements = syncy(pg.annotate(save_dir='shots'))
# elements = [{n, role, name, selector}] — pass img + elements to LLM
```

### Hidden JSON API

``` python
apis      = find_xhr('https://example.com/shop', pattern='*api*')
all_items = paginate_api(apis[0]['url'], payload=apis[0].get('request_body'),
                         results_field='items', max_pages=50)
```

### Browser automation

``` python
cdp = syncy(cdp_connect())
pg  = syncy(cdp.open_page('https://example.com/login'))
rt  = syncy(pg.ax_tree()); print(str(rt))   # print full tree; read [#N] IDs
syncy(pg.fill_text(123, 'user@example.com'))
syncy(pg.fill_text(456, 'mypassword'))
rt2 = syncy(pg.ax_tree()); print(str(rt2))  # re-read after every navigation; IDs change
syncy(pg.click_and_wait(789))
```

Always print `str(rt)` untruncated. Re-read `ax_tree()` after every
navigation. Never call `find_id()`. No `time.sleep()`.

------------------------------------------------------------------------

## CLI

All commands accept `--as_json`.

``` sh
fossick fetch <url> [--sel <css>] [--heavy] [--stealthy]
fossick search "<query>" [--n 10]
fossick read-arxiv <url-or-id> [--source] [--chars 4000]
fossick read-yt <url>
fossick search-yt "<query>" [--n 10]
fossick download-yt <url> [--format audio|video] [--save_dir .]
fossick url2nb <url> [--path out.ipynb]
fossick calls <url> [--pattern '.*'] [--tail 3]
fossick collect <url> [--save_dir .] [--tout N] [--count N] [--every_n N]
fossick annotate <url> [--save_dir .]
fossick start    # start SearXNG
fossick install  # register SKILL.md + safecmd allowlist
```

------------------------------------------------------------------------

## Gotchas

- `searxng_start()` required before `search()` — falls back to
  DuckDuckGo if Docker is unavailable
- `heavy=True` and CDP tools require Chrome — auto-launches but ~10s
  cold start; `stealthy=True` is slower, use only when a site actively
  blocks
- `fossick annotate` is interactive — browser must be visible; not for
  headless pipelines
- `read_arxiv()` returns 30-100k chars — always slice:
  `paper['source'][:8000]`
- `to_md()` without `sel=` includes nav/ads — always pass a content
  selector
