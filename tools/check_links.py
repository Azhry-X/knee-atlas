#!/usr/bin/env python3
"""Verify every link in the dossier PDF and the Atlas.

  python tools/check_links.py          # pre-deploy: Atlas anchors checked against local index.html
  python tools/check_links.py --live   # after GitHub Pages is live: also fetch the Atlas URL

Checks
  * Atlas anchors (#id) exist as cards in index.html
  * Ankle-atlas anchors exist on the live ankle atlas
  * External pages return HTTP 200 and are not a bot-check page (PMC needs a real browser:
    Playwright is used when installed, otherwise PMC links are reported as SKIPPED)
  * YouTube videos in tests.yaml still resolve via oEmbed
Exit code 1 on any failure.
"""
import sys, re, json, pathlib, urllib.request, urllib.parse
for _s in (sys.stdout, sys.stderr):  # Windows consoles: never crash on non-ASCII page titles
    try:
        _s.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'atlas'))
from config import ATLAS_BASE_URL  # noqa: E402
import yaml  # noqa: E402

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
      'Accept-Language': 'en-US,en;q=0.9'}
LIVE = '--live' in sys.argv


def pdf_links():
    from pypdf import PdfReader
    out = set()
    for pg in PdfReader(str(ROOT / 'master_knee_dossier.pdf')).pages:
        for a in pg.get('/Annots') or []:
            A = a.get_object().get('/A')
            if A is not None and A.get('/URI'):
                out.add(str(A['/URI']))
    return sorted(out)


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read(400000).decode('utf-8', 'ignore')
        m = re.search(r'<title[^>]*>(.*?)</title>', body, re.S | re.I)
        return r.status, (m.group(1).strip() if m else '')


def browser_titles(urls):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {u: None for u in urls}
    res = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(user_agent=UA['User-Agent'])
        for u in urls:
            pg = ctx.new_page()
            try:
                r = pg.goto(u, wait_until='domcontentloaded', timeout=45000)
                pg.wait_for_timeout(2500)
                res[u] = (r.status if r else 0, pg.title())
            except Exception as e:
                res[u] = (0, f'ERROR {e}')
            pg.close()
        b.close()
    return res


def main():
    fails, rows = [], []
    index = (ROOT / 'index.html').read_text(encoding='utf-8')
    card_ids = set(re.findall(r'<article class="card" id="([^"]+)"', index))
    links = pdf_links()
    pmc = [u for u in links if 'pmc.ncbi.nlm.nih.gov' in u]
    btitles = browser_titles(pmc) if pmc else {}
    for u in links:
        if u.startswith(ATLAS_BASE_URL):
            aid = u.split('#', 1)[1] if '#' in u else ''
            ok = aid in card_ids
            rows.append(('ATLAS', 'OK' if ok else 'MISSING CARD', u))
            if not ok:
                fails.append(u)
            continue
        if 'ankle-atlas' in u:
            aid = u.split('#', 1)[1]
            try:
                st, _ = fetch(u.split('#')[0])
                html = urllib.request.urlopen(urllib.request.Request(u.split('#')[0], headers=UA), timeout=30).read().decode('utf-8', 'ignore')
                ok = st == 200 and f'id="{aid}"' in html
            except Exception as e:
                ok = False
            rows.append(('ANKLE', 'OK' if ok else 'FAIL', u))
            if not ok:
                fails.append(u)
            continue
        if u in btitles:
            r = btitles[u]
            if r is None:
                rows.append(('PMC', 'SKIPPED (install playwright to verify)', u))
                continue
            st, title = r
            ok = st == 200 and 'recaptcha' not in title.lower() and title
            rows.append(('PMC', f'{st} {title[:70]}', u))
            if not ok:
                fails.append(u)
            continue
        try:
            st, title = fetch(u)
            ok = st == 200 and 'just a moment' not in title.lower()
            rows.append(('WEB', f'{st} {title[:70]}', u))
            if not ok:
                fails.append(u)
        except Exception as e:
            rows.append(('WEB', f'FAIL {e}', u))
            fails.append(u)
    # videos
    cards = yaml.safe_load((ROOT / 'atlas' / 'data' / 'tests.yaml').read_text(encoding='utf-8'))
    for c in cards:
        v = c.get('video_url')
        if not v:
            continue
        try:
            d = json.load(urllib.request.urlopen('https://www.youtube.com/oembed?format=json&url=' + urllib.parse.quote(v), timeout=30))
            rows.append(('VIDEO', f"OK {d['author_name']}: {d['title'][:60]}", c['id']))
        except Exception as e:
            rows.append(('VIDEO', f'FAIL {e}', c['id']))
            fails.append(v)
    if LIVE:
        try:
            st, title = fetch(ATLAS_BASE_URL + '/')
            rows.append(('LIVE', f'{st} {title}', ATLAS_BASE_URL))
            if st != 200:
                fails.append(ATLAS_BASE_URL)
        except Exception as e:
            rows.append(('LIVE', f'FAIL {e}', ATLAS_BASE_URL))
            fails.append(ATLAS_BASE_URL)
    for kind, status, u in rows:
        print(f'{kind:6} {status:60} {u}')
    print(f'\n{len(rows)} links checked, {len(fails)} failed')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
