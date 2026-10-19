"""Renderizador das artes ZeloKids (1024x1024, JPG q90).

uso: python3 render.py spec.json [--out-dir pasta]

spec.json = lista de imagens. Campos por imagem:
  out      nome do arquivo final (ex.: "trava-porta-bebe-macaneta-alavanca-01-capa.jpg")
  layout   "capa" | "hero" | "card" | "lista"
  img      caminho da foto (relativo ao spec.json)
  crop     [x0, y0, x1, y1] opcional: parte boa da foto (em px da foto original)
  t1, t2   título: t1 = linha leve, t2 = linha forte (qualquer um pode faltar)
  sub      texto de apoio (até 2 linhas; use \n para quebrar)
  icon     ícone ao lado do apoio (hero)
  items    lista: [{"icon": "check", "t": "título", "d": "descrição curta"}]
  style    lista: "num" (passos numerados) | "icon" (padrão)
  chips    card/hero: ["Banheiro", "Lavanderia", "Quarto"] com "chip_icons" opcional
  shield   true = escudo roxo pequeno no canto (hero/card)

Regras visuais (sistema-visual.md): roxo #5C54E9 em todo texto, verde #BAE150 só em detalhe,
fonte Lexend (300 leve / 700 forte / 400 apoio), fundo branco, sem corações, sem multicolor.
"""
import json, sys, pathlib, html, tempfile, shutil
from PIL import Image

KIT = pathlib.Path(__file__).resolve().parent
ROXO, VERDE = "#5C54E9", "#BAE150"
S = 1024

ICONS = {
 "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
 "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
 "lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
 "key": '<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M17 6l3 3M15 8l2 2"/>',
 "door": '<path d="M6 21V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v17"/><path d="M3 21h18"/><circle cx="14.5" cy="12" r="1.1" fill="currentColor"/>',
 "rotate": '<path d="M20 12a8 8 0 1 1-2.3-5.7"/><path d="M20 4v5h-5"/>',
 "nodrill": '<circle cx="12" cy="12" r="9"/><path d="M5.6 5.6l12.8 12.8"/><path d="M9 9h4l2 3"/>',
 "ruler": '<rect x="2.5" y="8" width="19" height="8" rx="1.5"/><path d="M6.5 8v3M10 8v4M13.5 8v3M17 8v4"/>',
 "button": '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="3.5"/>',
 "material": '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9L12 3z"/><path d="M12 12l8-4.5M12 12v9M12 12L4 7.5"/>',
 "bath": '<path d="M3 12h18v3a5 5 0 0 1-5 5H8a5 5 0 0 1-5-5v-3z"/><path d="M6 12V6a2 2 0 0 1 4 0"/>',
 "laundry": '<rect x="4" y="3" width="16" height="18" rx="2"/><circle cx="12" cy="13" r="4.5"/><path d="M7 6.5h2"/>',
 "bed": '<path d="M3 18V8M21 18v-5a3 3 0 0 0-3-3H10v5"/><path d="M3 15h18"/><circle cx="6.5" cy="11.5" r="1.5"/>',
 "baby": '<circle cx="12" cy="13" r="8"/><path d="M12 5c-1.5 0-2 1-1.5 2"/><circle cx="9.3" cy="12.5" r=".8" fill="currentColor"/><circle cx="14.7" cy="12.5" r=".8" fill="currentColor"/><path d="M9.5 15.5c1.4 1.3 3.6 1.3 5 0"/>',
 "question": '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .8-1 1.5v.7"/><circle cx="12" cy="17" r=".9" fill="currentColor"/>',
 "heartless_star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9L12 3z"/>',
}

def svg(name, size=24, color="currentColor", sw=2):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')

def esc(t):
    return html.escape(t or "").replace("\n", "<br>")

def prep_image(src, dst, crop=None, box=None, whiten=False, trim=False):
    im = Image.open(src).convert("RGB")
    if crop: im = im.crop(tuple(crop))
    if box:  # recorta no centro para a proporção da caixa
        bw, bh = box; r = bw / bh
        w, h = im.size
        if w / h > r:
            nw = int(h * r); x = (w - nw) // 2; im = im.crop((x, 0, x + nw, h))
        else:
            nh = int(w / r); y = (h - nh) // 2; im = im.crop((0, y, w, y + nh))
        im = im.resize((bw * 2, bh * 2), Image.LANCZOS)
    if whiten:  # fundo quase branco vira branco puro (capa)
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                r, g, b = px[x, y]
                if r > 242 and g > 242 and b > 242: px[x, y] = (255, 255, 255)
        if trim:  # corta a margem branca para o produto ocupar mais espaço
            from PIL import ImageChops
            bbox = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
            if bbox:
                p = 16; im = im.crop((max(bbox[0]-p, 0), max(bbox[1]-p, 0), min(bbox[2]+p, im.width), min(bbox[3]+p, im.height)))
    im.save(dst, "PNG")

CSS = f"""
@font-face{{font-family:'Lexend';src:url('lexend.woff2') format('woff2');font-weight:100 900}}
html,body{{margin:0;padding:0}}
.art{{width:{S}px;height:{S}px;position:relative;overflow:hidden;font-family:'Lexend',sans-serif;color:{ROXO};background:#fff}}
.title{{position:absolute;left:0;width:{S}px;display:flex;flex-direction:column;align-items:center;text-align:center;gap:0}}
.t1{{font-size:74px;font-weight:300;line-height:1.06;letter-spacing:-1px;white-space:nowrap}}
.t2{{font-size:74px;font-weight:700;line-height:1.06;letter-spacing:-1.5px;white-space:nowrap}}
.sub{{font-size:29px;font-weight:400;line-height:1.32;color:{ROXO}}}
.shield{{position:absolute;width:84px;height:84px;border-radius:50%;background:{ROXO};border:5px solid #fff;
  box-shadow:0 8px 20px rgba(92,84,233,.28);display:flex;align-items:center;justify-content:center}}
.chips{{position:absolute;display:flex;gap:14px;justify-content:center;left:0;width:{S}px}}
.chip{{display:flex;align-items:center;gap:10px;background:#fff;color:{ROXO};border-radius:999px;padding:14px 26px;
  font-size:26px;font-weight:600;box-shadow:0 6px 18px rgba(45,40,100,.16)}}
.card{{position:absolute;overflow:hidden;border-radius:36px;background:#F4F3F0}}
.card img{{width:100%;height:100%;object-fit:cover;display:block}}
.items{{display:flex;flex-direction:column;gap:30px}}
.it{{display:flex;gap:22px;align-items:flex-start}}
.ic{{flex:0 0 64px;height:64px;border-radius:50%;background:{ROXO};color:#fff;display:flex;align-items:center;justify-content:center;
  font-size:30px;font-weight:700}}
.it b{{display:block;font-size:30px;font-weight:600;line-height:1.2}}
.it span{{display:block;font-size:23px;font-weight:400;line-height:1.35;margin-top:4px;opacity:.92}}
"""

FIT_JS = """
document.querySelectorAll('.t1,.t2').forEach(e=>{let s=parseFloat(getComputedStyle(e).fontSize);
  while(e.scrollWidth>930&&s>40){s-=2;e.style.fontSize=s+'px';}});
"""

def title_block(sp, top):
    t = ""
    if sp.get("t1"): t += f'<span class="t1">{esc(sp["t1"])}</span>'
    if sp.get("t2"): t += f'<span class="t2">{esc(sp["t2"])}</span>'
    return f'<div class="title" style="top:{top}px">{t}</div>'

def chips_html(sp, bottom):
    if not sp.get("chips"): return ""
    icons = sp.get("chip_icons") or [None] * len(sp["chips"])
    c = "".join(f'<span class="chip">{svg(i, 28) if i else ""}{esc(t)}</span>' for t, i in zip(sp["chips"], icons))
    return f'<div class="chips" style="bottom:{bottom}px">{c}</div>'

def shield_html(sp, left, bottom):
    if not sp.get("shield"): return ""
    return (f'<div class="shield" style="left:{left}px;bottom:{bottom}px">'
            f'<svg width="42" height="42" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z"/><path d="M8.5 12l2.5 2.5 4.5-5" stroke="{VERDE}"/></svg></div>')

def build(sp, work, base):
    lay = sp["layout"]; src = base / sp["img"]
    if lay == "capa":
        prep_image(src, work / "img.png", sp.get("crop"), whiten=True)
        body = '<img src="img.png" style="position:absolute;left:62px;top:62px;width:900px;height:900px;object-fit:contain">'
    elif lay == "hero":
        prep_image(src, work / "img.png", sp.get("crop"), box=(S, S))
        sub = ""
        if sp.get("sub"):
            ic = svg(sp["icon"], 64, sw=1.6) if sp.get("icon") else ""
            sub = (f'<div style="position:absolute;top:{300 if sp.get("t1") and sp.get("t2") else 210}px;left:0;width:{S}px;display:flex;'
                   f'justify-content:center;align-items:center;gap:20px">{ic}<p class="sub" style="margin:0;text-align:left">{esc(sp["sub"])}</p></div>')
        body = (f'<img src="img.png" style="position:absolute;inset:0;width:{S}px;height:{S}px;object-fit:cover">'
                f'<div style="position:absolute;left:0;top:0;width:{S}px;height:430px;background:linear-gradient(180deg,rgba(255,255,255,.92) 0%,rgba(255,255,255,.62) 62%,rgba(255,255,255,0) 100%)"></div>'
                + title_block(sp, 70) + sub + chips_html(sp, 56) + shield_html(sp, 56, 56))
    elif lay == "card":
        two = sp.get("t1") and sp.get("t2")
        sub_top = 232 if two else 150
        card_top = sub_top + (118 if sp.get("sub") else 36)
        ch = S - card_top - 50
        prep_image(src, work / "img.png", sp.get("crop"), box=(924, ch))
        sub = f'<p class="sub" style="position:absolute;top:{sub_top}px;left:0;width:{S}px;margin:0;text-align:center">{esc(sp.get("sub"))}</p>' if sp.get("sub") else ""
        body = (title_block(sp, 58) + sub +
                f'<div class="card" style="left:50px;top:{card_top}px;width:924px;height:{ch}px"><img src="img.png"></div>'
                + chips_html(sp, 84) + shield_html(sp, 78, 78))
    elif lay == "lista":
        two = sp.get("t1") and sp.get("t2")
        top = 300 if two else 214
        w = sp.get("img", "").endswith("capa.png")  # foto da capa: fundo branco, margem cortada, encaixe sem corte
        prep_image(src, work / "img.png", sp.get("crop"), whiten=w, trim=w)
        num = sp.get("style") == "num"
        its = ""
        for i, it in enumerate(sp["items"], 1):
            mark = str(i) if num else svg(it.get("icon", "check"), 34, "#fff", 2.2)
            desc = f'<span>{esc(it["d"])}</span>' if it.get("d") else ""
            its += f'<div class="it"><div class="ic">{mark}</div><div><b>{esc(it["t"])}</b>{desc}</div></div>'
        body = (title_block(sp, 58) +
                f'<div class="card" style="left:40px;top:{top}px;width:430px;height:{S - top - 60}px;background:#fff"><img src="img.png" style="object-fit:contain"></div>'
                f'<div class="items" style="position:absolute;left:500px;top:{top}px;width:480px;height:{S - top - 60}px;justify-content:center">{its}</div>')
    else:
        raise SystemExit(f"layout desconhecido: {lay}")
    return f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="art">{body}</div></body></html>'

def main():
    spec_path = pathlib.Path(sys.argv[1]).resolve()
    out_dir = pathlib.Path(sys.argv[sys.argv.index("--out-dir") + 1]).resolve() if "--out-dir" in sys.argv else spec_path.parent / "final"
    out_dir.mkdir(parents=True, exist_ok=True)
    specs = json.loads(spec_path.read_text(encoding="utf-8"))
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": S, "height": S})
        for sp in specs:
            work = pathlib.Path(tempfile.mkdtemp())
            shutil.copy(KIT / "fonts" / "lexend.woff2", work / "lexend.woff2")
            (work / "a.html").write_text(build(sp, work, spec_path.parent), encoding="utf-8")
            pg.goto((work / "a.html").as_uri()); pg.evaluate("document.fonts.ready"); pg.evaluate(FIT_JS)
            pg.wait_for_timeout(150)
            tmp = work / "o.png"; pg.locator(".art").screenshot(path=str(tmp))
            Image.open(tmp).convert("RGB").save(out_dir / sp["out"], quality=90, optimize=True)
            print("ok", sp["out"])
        b.close()

if __name__ == "__main__":
    main()
