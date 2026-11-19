"""Temporary: probe candidate listing URLs and print what they show."""
import json, time
from playwright.sync_api import sync_playwright

URLS = [
    "https://jobsireland.ie/",
    "https://jobsireland.ie/en-US/job-search",
    "https://stafflinerecruit.com/",
    "https://stafflinerecruit.com/jobs",
    "https://www.ucc.ie/en/compsci/vacancies",
    "https://ore.ucc.ie/",
    "https://www.ucc.ie/en/hr/vacancies/",
    "https://universityvacancies.com/",
    "https://universityvacancies.com/institutions",
    "https://www.ul.ie/hr/vacancies",
    "https://www.mtu.ie/vacancies/",
    "https://www.setu.ie/about/jobs",
]
JS = r"""() => {
  const t = (document.body ? document.body.innerText : '') || '';
  const seen = new Set(); const links = [];
  for (const a of document.querySelectorAll('a[href]')) {
    const s = (a.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 60);
    if (!/job|vacanc|search|career|garda|public|academic|lectur|institution|browse|all /i.test(s + ' ' + a.href)) continue;
    if (seen.has(a.href) || a.href.startsWith('javascript')) continue;
    seen.add(a.href); links.push(s + ' => ' + a.href);
    if (links.length >= 30) break;
  }
  return {title: document.title, url: location.href, textLen: t.length,
          forms: document.querySelectorAll('form').length, inputs: Array.from(document.querySelectorAll('input[name],select[name]')).map(i => i.name).slice(0, 15),
          head: t.replace(/\n{2,}/g, '\n').slice(0, 500), links};
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
            print(json.dumps(page.evaluate(JS), indent=1, ensure_ascii=False)[:4500])
        except Exception as e:
            print("ERR", type(e).__name__, str(e)[:160])
        ctx.close(); time.sleep(3)
    b.close()
