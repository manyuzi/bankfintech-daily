
import os, json, csv, hashlib, datetime as dt, pathlib, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ARCH = DOCS / "archive"
DATA = DOCS / "data"
ASSETS = DOCS / "assets"
TEMPLATE = ROOT / "templates" / "page.html.j2"

SCHEDULE = os.environ.get("DAILY_SCHEDULE","00:30 UTC / 08:30 Beijing")

def fingerprint(item):
    d = (item.get("publish_time","") or "")[:10]
    key = f"{item.get('source','')}|{item.get('title','')}|{d}"
    return hashlib.md5(key.encode("utf-8")).hexdigest()

def ensure_dirs():
    for p in [DOCS, ARCH, DATA, ASSETS]:
        p.mkdir(parents=True, exist_ok=True)

def load_sources():
    try:
        return json.load(open(ROOT/'data'/'sources.json','r',encoding='utf-8'))
    except Exception:
        return []

def fetch_items():
    items = []
    for s in load_sources():
        url = s.get("url") or ""
        if not url or url.startswith("<"):  # placeholder
            continue
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                raw = resp.read().decode("utf-8","ignore")
                data = json.loads(raw)
                arr = data.get("items", data if isinstance(data, list) else [])
                for it in arr:
                    items.append({
                        "source": s.get("name") or it.get("source") or "",
                        "title": (it.get("title") or "").strip(),
                        "summary": it.get("summary") or it.get("desc") or it.get("excerpt") or "",
                        "link": it.get("link") or it.get("url") or "",
                        "publish_time": it.get("publish_time") or it.get("pubDate") or it.get("date") or ""
                    })
        except Exception as e:
            print("[warn] fetch fail", s.get("name"), e)
    return items

def load_sample():
    return json.load(open(ROOT/'data'/'sample_data.json','r',encoding='utf-8'))

def render_html(date_str, items):
    tpl = open(TEMPLATE,'r',encoding='utf-8').read()
    cards = []
    for r in items:
        tags = r.get("tags") or []
        idea_outline = r.get("idea_outline") or []
        tag_html = "".join([f'<span class="tag">{t}</span>' for t in tags])
        outline_html = "".join([f"<li>{o}</li>" for o in idea_outline])
        card = f'''
        <div class="card">
          <h2>{r.get("idea_title") or r.get("title")}</h2>
          <div class="meta">来源：{r.get("source","")} · 发布：{(r.get("publish_time","") or "")[:19]}</div>
          <div class="kv">{tag_html}</div>
          <div class="meta">摘要：{r.get("summary","")}</div>
          <ol class="ol">{outline_html}</ol>
          <div class="meta">原文：<a href="{r.get("link","")}" target="_blank">{r.get("title","")}</a></div>
        </div>
        '''
        cards.append(card)
    return tpl.format(date=date_str, cards="\n".join(cards), schedule=SCHEDULE)

def write_json(date_str, items):
    p = DATA / f"{date_str}.json"
    json.dump(items, open(p,'w',encoding='utf-8'), ensure_ascii=False, indent=2)

def write_csv(date_str, items):
    p = DATA / f"{date_str}.csv"
    with open(p, "w", encoding="utf-8", newline="") as f:
        w=csv.writer(f)
        w.writerow(["source","title","tags","idea_title","idea_outline","publish_time","link"])
        for r in items:
            w.writerow([
                r.get("source",""),
                r.get("title",""),
                "、".join(r.get("tags") or []),
                r.get("idea_title",""),
                " | ".join(r.get("idea_outline") or []),
                (r.get("publish_time","") or "")[:19],
                r.get("link","")
            ])

def main():
    ensure_dirs()
    date_str = dt.datetime.utcnow().date().isoformat()
    items = fetch_items()
    if not items:
        items = load_sample()

    # Deduplicate
    seen=set(); uniq=[]
    for it in items:
        fp = fingerprint(it)
        if fp in seen: continue
        seen.add(fp); uniq.append(it)

    # Fill defaults for sample
    for r in uniq:
        r.setdefault("tags", ["行业观察"])
        r.setdefault("idea_title", f"从《{r.get('title','')}》看落地路径")
        r.setdefault("idea_outline", ["要点速读","适配点","落地清单","风控与合规","ROI"])

    html = render_html(date_str, uniq)
    # write files
    (ROOT/'docs'/'index.html').write_text(html, encoding='utf-8')
    (ROOT/'docs'/'archive').mkdir(exist_ok=True, parents=True)
    (ROOT/'docs'/'archive'/f"{date_str}.html").write_text(html, encoding='utf-8')
    (ROOT/'docs'/'data').mkdir(exist_ok=True, parents=True)
    write_json(date_str, uniq)
    write_csv(date_str, uniq)

    print("Generated for", date_str)

if __name__ == "__main__":
    main()
