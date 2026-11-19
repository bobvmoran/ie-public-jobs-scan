"""Weekly read-only scan of Irish public sector job listing pages.

Opens each page in sources.py with a headless browser, lets its scripts run,
and saves the visible text plus the job-like links to data/pages/<slug>.md.
data/index.json records what loaded and what didn't.

It only reads public pages. It never signs in, fills forms, or gets around
blocks: a login wall, 403 or CAPTCHA is recorded as "blocked" and skipped.
"""

import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

sys.path.insert(0, str(Path(__file__).parent))
from sources import SOURCES  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data"
PAGES = OUT / "pages"

MAX_TEXT = 30_000          # characters of text kept per result page
PAUSE_SECONDS = 4          # pause between page loads, to browse at a normal pace
NAV_TIMEOUT_MS = 45_000

KEYWORDS = re.compile(
    r"\b(data|digital|ict|i\.t\.|ai|artificial intelligence|machine learning|analytic|"
    r"technolog|information|architect|cyber|statistic|software|computing|computer|"
    r"engineer|platform|transformation|lecturer|professor|principal|head of|manager|"
    r"grade vii|grade viii|director|chief|officer|specialist|programme|project)",
    re.I,
)
BLOCK_SIGNS = re.compile(
    r"(access denied|are you a robot|verify you are human|captcha|cf-challenge|"
    r"request unsuccessful|attention required|please enable cookies|unusual traffic)",
    re.I,
)
NEXT_RE = re.compile(r"^\s*(next(\s+page)?(\s*[›»>])?|[›»])\s*$", re.I)


# Page text without the search-filter clutter: drop-down options and long
# tick-box lists (the HSE search has ~960) otherwise fill the page before the
# job listings start. Elements are hidden only while the text is read.
TEXT_JS = """() => {
  if (!document.body) return '';
  const hidden = [];
  const hide = el => { hidden.push([el, el.style.display]); el.style.display = 'none'; };
  document.querySelectorAll('select').forEach(hide);
  const ticks = document.querySelectorAll('input[type=checkbox], input[type=radio]');
  if (ticks.length > 15) ticks.forEach(i => (i.labels || []).forEach(hide));
  const text = document.body.innerText || '';
  hidden.forEach(([el, d]) => { el.style.display = d; });
  return text;
}"""


def page_payload(page):
    text = page.evaluate(TEXT_JS) or ""
    links = page.evaluate(
        """() => Array.from(document.querySelectorAll('a[href]')).map(a => ({
              text: (a.innerText || a.getAttribute('aria-label') || '').trim(),
              href: a.href }))"""
    )
    seen, keep = set(), []
    for link in links:
        h = link["href"]
        lines = [" ".join(ln.split()) for ln in link["text"].splitlines() if ln.strip()]
        if not lines or h in seen or h.startswith(("javascript:", "mailto:", "tel:")):
            continue
        t = " ".join(lines)
        if len(t) > 200:          # a whole job card wrapped in one link: keep its heading
            t = lines[0][:200]
        if KEYWORDS.search(t):
            seen.add(h)
            keep.append({"text": t, "href": h})
    return re.sub(r"\n{3,}", "\n\n", text).strip(), keep


def click_next(page, next_number):
    """Go to the next results page: the pager's Next link, or failing that the
    link for the next page number. Returns False when there is nowhere to go."""
    candidates = (
        page.get_by_role("link", name=NEXT_RE),
        page.locator("a").filter(has_text=NEXT_RE),
        page.get_by_role("button", name=NEXT_RE),   # pagers built from buttons (Staffline)
        page.get_by_role("link", name=str(next_number), exact=True),
    )
    for loc in candidates:
        for i in range(min(loc.count(), 5)):
            el = loc.nth(i)
            if not el.is_visible():
                continue
            if el.get_attribute("aria-disabled") == "true" or "disabled" in (el.get_attribute("class") or ""):
                continue
            if not el.is_enabled():
                continue
            href = (el.get_attribute("href") or "").strip()
            try:
                if href and not href.startswith(("#", "javascript:")):
                    # an ordinary link: open it directly (a cookie banner can sit over the pager)
                    page.goto(urljoin(page.url, href), wait_until="domcontentloaded")
                else:
                    el.click(timeout=10_000)
            except Exception:
                return False  # keep the pages already read
            return True
    return False


def scan_source(browser, src):
    result = {
        "slug": src["slug"], "name": src["name"], "url": src["url"],
        "status": "ok", "http_status": None, "error": None,
        "pages_read": 0, "links_found": 0, "chars": 0,
    }
    ctx = browser.new_context(locale="en-IE", timezone_id="Europe/Dublin")
    page = ctx.new_page()
    page.set_default_timeout(NAV_TIMEOUT_MS)
    texts, links, last_text = [], [], None
    try:
        resp = page.goto(src["url"], wait_until="domcontentloaded")
        result["http_status"] = resp.status if resp else None
        for n in range(src.get("pages", 1)):
            try:
                page.wait_for_load_state("networkidle", timeout=15_000)
            except PWTimeout:
                pass  # some sites keep polling; take what has rendered
            text, found = page_payload(page)
            status = result["http_status"] or 200
            if BLOCK_SIGNS.search(text[:3000]) or status in (401, 403, 429):
                result["status"] = "blocked"
                break
            if status >= 400:
                result["status"] = "error"
                result["error"] = f"HTTP {status} (page not found or server error)"
                break
            if texts and text == last_text:
                break  # the pager did not move on; stop rather than save a repeat
            last_text = text
            texts.append(f"--- page {n + 1}: {page.url} ---\n{text[:MAX_TEXT]}")
            links.extend(found)
            result["pages_read"] = n + 1
            if n + 1 < src.get("pages", 1):
                if not click_next(page, n + 2):
                    break
                time.sleep(PAUSE_SECONDS)
    except Exception as exc:  # record and move on
        result["status"] = "error"
        result["error"] = f"{type(exc).__name__}: {str(exc)[:300]}"
    finally:
        ctx.close()

    body = "\n\n".join(texts)
    dedup = list({l["href"]: l for l in links}.values())
    result["links_found"], result["chars"] = len(dedup), len(body)
    if result["status"] == "ok" and len(body) < 200:
        result["status"] = "empty"

    md = [
        f"# {src['name']}",
        f"URL: {src['url']}",
        f"Fetched: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"Status: {result['status']} (HTTP {result['http_status']}), pages read: {result['pages_read']}",
    ]
    if result["error"]:
        md.append(f"Error: {result['error']}")
    md += ["", "## Job-like links", *[f"- [{l['text']}]({l['href']})" for l in dedup],
           "", "## Page text", body]
    (PAGES / f"{src['slug']}.md").write_text("\n".join(md), encoding="utf-8")
    return result


def main():
    PAGES.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])  # optional: python scrape.py hse-limerick tus
    sources = [s for s in SOURCES if not only or s["slug"] in only]
    started = datetime.now(timezone.utc)
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for i, src in enumerate(sources):
            if i:
                time.sleep(PAUSE_SECONDS)
            r = scan_source(browser, src)
            print(f"{r['status']:8} {r['slug']:32} links={r['links_found']:4} chars={r['chars']}")
            results.append(r)
        browser.close()
    index = {
        "run_started": started.isoformat(timespec="seconds"),
        "run_finished": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "page_file_pattern": "data/pages/<slug>.md",
        "sources": results,
    }
    (OUT / "index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    if not only:  # full run: drop saved pages for sources no longer in the list
        keep = {f"{s['slug']}.md" for s in SOURCES} | {".gitkeep"}
        for f in PAGES.iterdir():
            if f.name not in keep:
                f.unlink()


if __name__ == "__main__":
    main()
