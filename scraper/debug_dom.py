"""Temporary: probe search URL forms."""
import json, re, time
from playwright.sync_api import sync_playwright

URLS = [
    "https://jobsireland.ie/search-jobs?keyword=data",
    "https://jobsireland.ie/search-jobs?search=data",
    "https://jobsireland.ie/search-jobs?q=data",
    "https://stafflinerecruit.com/jobs?country%5B0%5D=Republic%20of%20Ireland",
    "https://stafflinerecruit.com/jobs?search=garda",
    "https://stafflinerecruit.com/jobs?search_terms=garda",
    "https://stafflinerecruit.com/jobs/employers",
]
JS = r"""() => {
  const t = ((document.body ? document.body.innerText : '') || '').replace(/\n{2,}/g, '\n');
  const i = t.search(/Jobs Available|Showing/);
  const pager = Array.from(document.querySelectorAll('a,button')).map(a => [(a.innerText||'').trim().slice(0,30), a.getAttribute('aria-label'), a.getAttribute('href'), a.tagName]).filter(x => /^(next.*|\d{1,2}|›|»|>|load more.*|show more.*)$/i.test(x[0]) || /next|page/i.test(x[1]||'')).slice(0, 12);
  const garda = Array.from(document.querySelectorAll('a[href],option')).filter(a => /garda|public sector/i.test(a.innerText||a.textContent||'')).map(a => [(a.innerText||a.textContent).trim().slice(0,70), a.href || a.value]).slice(0, 12);
  const inputs = Array.from(document.querySelectorAll('input')).filter(i => i.offsetWidth).map(i => [i.type, i.name, i.placeholder, i.id]).slice(0, 8);
  return {url: location.href, textLen: t.length, around: t.slice(Math.max(0, i), Math.max(0, i) + 700), pager, garda, inputs};
}"""
with sync_playwright() as p:
    b = p.chromium.launch()
    for u in URLS:
        ctx = b.new_context(locale="en-IE", timezone_id="Europe/Dublin"); page = ctx.new_page()
        print("=====", u)
        try:
            r = page.goto(u, wait_until="domcontentloaded", timeout=45000)
            try: page.wait_for_load_state("networkidle", timeout=12000)
            except Exception: pass
            print("status", r.status if r else None)
            print(json.dumps(page.evaluate(JS), indent=1, ensure_ascii=False)[:3500])
        except Exception as e:
            print("ERR", type(e).__name__, str(e)[:160])
        ctx.close(); time.sleep(3)
    # jobsireland: type in the public search box and see what URL results
    ctx = b.new_context(locale="en-IE", timezone_id="Europe/Dublin"); page = ctx.new_page()
    print("===== jobsireland search box")
    reqs = []
    page.on("request", lambda q: reqs.append(q.method + " " + q.url[:200]) if q.resource_type in ("xhr", "fetch") else None)
    try:
        page.goto("https://jobsireland.ie/search-jobs", wait_until="domcontentloaded", timeout=45000)
        try: page.wait_for_load_state("networkidle", timeout=12000)
        except Exception: pass
        box = page.locator("input:visible").first
        box.fill("data analyst"); box.press("Enter")
        time.sleep(6)
        print("url after search:", page.url)
        print(json.dumps(page.evaluate(JS), indent=1, ensure_ascii=False)[:1800])
        print("xhr:", json.dumps(reqs[-12:], indent=1))
    except Exception as e:
        print("ERR", type(e).__name__, str(e)[:200])
    ctx.close(); b.close()
