"""Renderizador das artes ZeloKids (1024x1024, JPG q90) — v2 (render em 2K, layouts variados, zoom de detalhe).

uso: python3 render.py spec.json [--out-dir pasta] [--only 01,06]

spec.json = lista de imagens. Campos por imagem:
  out      nome do arquivo final (ex.: "trava-porta-bebe-macaneta-alavanca-01-capa.jpg")
  layout   "capa" | "hero" | "overlay" | "card" | "split" | "lista" | "passos" | "detalhe"
  img      caminho da foto (relativo ao spec.json). Se existir a mesma foto em `_fontes/pro-2k/`, ela é usada (2048 px).
  crop     [x0, y0, x1, y1] opcional: parte boa da foto (em px da foto de 1024)
  t1, t2   título: t1 = linha leve (Rubik 300), t2 = linha forte (Capriola)
  sub      texto de apoio (até 2 linhas; use \\n para quebrar)
  icon     ícone ao lado do apoio (hero/split)
  items    lista: [{"icon": "check", "t": "título", "d": "descrição curta"}]
  style    lista/passos: "num" (numerados) | "icon" (padrão)
  side     lista/split: "left" (foto à esquerda, padrão) | "right" (foto à direita)
  chips    card/hero/overlay: ["Banheiro", "Lavanderia"] com "chip_icons" opcional
  shield   true = escudo roxo pequeno no canto
  white    true = foto de estúdio: fundo vira branco puro e margem é cortada
  markers  lista: [{"n":1,"x":0.3,"y":0.1}] círculos numerados sobre a foto (fração da foto)
  zooms    detalhe: [{"n":1,"x":0.3,"y":0.1,"at":[0.15,0.4],"zoom":2.4}] lupa circular com o ponto (x,y) da foto
           ampliado, posicionada em `at` (fração do quadro) e ligada ao ponto por uma linha fina

Regras visuais (sistema-visual.md): roxo #5C54E9 em todo texto, verde #BAE150 só em detalhe,
Capriola (título forte) + Rubik (linha leve, apoio, itens), fundo branco, sem corações, sem multicolor.
A arte é renderizada em 2048 px e reduzida para 1024 (Lanczos + nitidez leve): textos e fotos ficam nítidos.
"""
import json, sys, pathlib, html, tempfile, shutil, math
from PIL import Image, ImageFilter

KIT = pathlib.Path(__file__).resolve().parent
ROXO, VERDE = "#5C54E9", "#BAE150"
S = 1024
SCALE = 2  # render em 2048 e reduz

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
 "bag": '<path d="M5 8h14l-1 12H6L5 8z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/>',
 "car": '<path d="M4 15l1.5-5.5A2 2 0 0 1 7.4 8h9.2a2 2 0 0 1 1.9 1.5L20 15"/><rect x="3" y="15" width="18" height="4" rx="1.5"/><circle cx="7.5" cy="19.5" r="1.5"/><circle cx="16.5" cy="19.5" r="1.5"/>',
 "home": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>',
 "drop": '<path d="M12 3s-6 6.5-6 11a6 6 0 0 0 12 0c0-4.5-6-11-6-11z"/>',
 "sound_off": '<path d="M4 9h3l5-4v14l-5-4H4z"/><path d="M16 9l5 6M21 9l-5 6"/>',
 "wash": '<path d="M4 10c2-2 4-2 6 0s4 2 6 0 4-2 6 0"/><path d="M4 15c2-2 4-2 6 0s4 2 6 0 4-2 6 0"/>',
}

def svg(name, size=24, color="currentColor", sw=2):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')

def esc(t):
    return html.escape(t or "").replace("\n", "<br>")

def source(base, rel):
    """Usa a versão 2K (`_fontes/pro-2k/<nome>`) quando existir."""
    p = base / rel
    hi = p.parent / "pro-2k" / p.name
    return hi if hi.exists() else p

def load(src, crop=None):
    im = Image.open(src).convert("RGB")
    if crop:  # crop é dado em px da foto de 1024; escala para a resolução real
        k = im.width / 1024
        im = im.crop(tuple(int(v * k) for v in crop))
    return im

def whiten_trim(im, trim=True):
    """Só o FUNDO (região clara ligada às bordas) vira branco puro; o produto não é tocado."""
    import numpy as np
    from scipy import ndimage
    a = np.array(im).astype(int)
    corners = np.array([a[0, 0], a[0, -1], a[-1, 0], a[-1, -1]])
    bg = np.median(corners, axis=0)
    if bg.min() >= 215:
        cand = (np.abs(a - bg).max(axis=2) <= 10)
        lab, n = ndimage.label(cand)
        border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
        m = np.isin(lab, list(border))
        m = ndimage.binary_erosion(m, iterations=1)
        soft = ndimage.gaussian_filter(m.astype(float), 1.0 * (im.width / 1024))[..., None]
        out = a * (1 - soft) + 255 * soft
        im = Image.fromarray(out.clip(0, 255).astype("uint8"))
    if trim:
        from PIL import ImageChops
        diff = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).convert("L").point(lambda v: 255 if v > 8 else 0)
        bbox = diff.getbbox()
        if bbox:
            p = int(16 * im.width / 1024)
            im = im.crop((max(bbox[0]-p, 0), max(bbox[1]-p, 0), min(bbox[2]+p, im.width), min(bbox[3]+p, im.height)))
    return im

def fit_box(im, bw, bh):
    """Recorta no centro para a proporção (bw x bh) e devolve em 2x."""
    r = bw / bh; w, h = im.size
    if w / h > r:
        nw = int(h * r); x = (w - nw) // 2; im = im.crop((x, 0, x + nw, h))
    else:
        nh = int(w / r); y = (h - nh) // 2; im = im.crop((0, y, w, y + nh))
    return im.resize((bw * SCALE, bh * SCALE), Image.LANCZOS)

def save(im, path):
    im.save(path, "PNG")

# Tipografia da marca: Capriola (títulos) + Rubik (linha leve do título, apoio, itens)
FONT_FILES = [KIT / "fonts" / "capriola.woff2", KIT / "fonts" / "rubik.woff2"]
FONT_FACE = ("@font-face{font-family:'Capriola';src:url('capriola.woff2') format('woff2');font-weight:400}"
             "@font-face{font-family:'Rubik';src:url('rubik.woff2') format('woff2');font-weight:300 900}")

CSS = f"""
{FONT_FACE}
html,body{{margin:0;padding:0}}
.art{{width:{S}px;height:{S}px;position:relative;overflow:hidden;font-family:'Rubik',sans-serif;color:{ROXO};background:#fff}}
.bar{{width:76px;height:7px;border-radius:4px;background:{VERDE};margin-top:14px}}
.mk{{position:absolute;width:46px;height:46px;margin:-23px 0 0 -23px;border-radius:50%;background:{ROXO};color:#fff;border:4px solid {VERDE};
  display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:700;box-shadow:0 6px 16px rgba(45,40,100,.3);z-index:3}}
.title{{position:absolute;left:0;width:{S}px;display:flex;flex-direction:column;align-items:center;text-align:center;gap:0}}
.title.left{{align-items:flex-start;text-align:left}}
.t1{{font-family:'Rubik',sans-serif;font-size:70px;font-weight:300;line-height:1.08;letter-spacing:-1px;white-space:nowrap}}
.t2{{font-family:'Capriola',sans-serif;font-size:72px;font-weight:400;line-height:1.08;letter-spacing:-1px;white-space:nowrap}}
.sub{{font-size:29px;font-weight:400;line-height:1.32;color:{ROXO}}}
.shield{{position:absolute;width:84px;height:84px;border-radius:50%;background:{ROXO};border:5px solid #fff;
  box-shadow:0 8px 20px rgba(92,84,233,.28);display:flex;align-items:center;justify-content:center;z-index:4}}
.chips{{position:absolute;display:flex;gap:14px;justify-content:center;left:0;width:{S}px;z-index:4}}
.chip{{display:flex;align-items:center;gap:10px;background:{ROXO};color:#fff;border-radius:999px;padding:14px 26px;
  font-size:26px;font-weight:600;box-shadow:0 6px 18px rgba(45,40,100,.22)}}
.chip svg{{color:{VERDE}}}
.card{{position:absolute;overflow:hidden;border-radius:36px;background:#F4F3F0}}
.card img{{width:100%;height:100%;object-fit:cover;display:block}}
.items{{display:flex;flex-direction:column;gap:30px}}
.it{{display:flex;gap:22px;align-items:flex-start}}
.ic{{flex:0 0 64px;width:64px;height:64px;box-sizing:border-box;border-radius:50%;background:{ROXO};color:#fff;display:flex;align-items:center;justify-content:center;
  font-size:30px;font-weight:700}}
.ic.num{{border:4px solid {VERDE}}}
.it b{{display:block;font-size:30px;font-weight:600;line-height:1.2}}
.it span{{display:block;font-size:23px;font-weight:400;line-height:1.35;margin-top:4px;opacity:.92}}
.zoom{{position:absolute;border-radius:50%;overflow:hidden;border:6px solid {VERDE};box-shadow:0 10px 28px rgba(45,40,100,.22);background:#fff;z-index:3}}
.zoom img{{position:absolute;display:block}}
.zn{{position:absolute;width:52px;height:52px;border-radius:50%;background:{ROXO};color:#fff;border:4px solid #fff;display:flex;align-items:center;justify-content:center;
  font-size:25px;font-weight:700;z-index:5;box-shadow:0 6px 16px rgba(45,40,100,.3)}}
"""

FIT_JS = """
document.querySelectorAll('.t1,.t2').forEach(e=>{let s=parseFloat(getComputedStyle(e).fontSize);
  const max=parseFloat(e.dataset.max||930);
  while(e.scrollWidth>max&&s>40){s-=2;e.style.fontSize=s+'px';}});
"""

def page(body):
    return f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="art">{body}</div></body></html>'

def title_block(sp, top, left=None, width=None, bar=True, max_w=930):
    t = ""
    if sp.get("t1"): t += f'<span class="t1" data-max="{max_w}">{esc(sp["t1"])}</span>'
    if sp.get("t2"): t += f'<span class="t2" data-max="{max_w}">{esc(sp["t2"])}</span>'
    if bar: t += '<span class="bar"></span>'
    cls = "title left" if left is not None else "title"
    pos = f'top:{top}px' + (f';left:{left}px;width:{width}px' if left is not None else "")
    return f'<div class="{cls}" style="{pos}">{t}</div>'

def chips_html(sp, bottom, left=0, width=S):
    if not sp.get("chips"): return ""
    icons = sp.get("chip_icons") or [None] * len(sp["chips"])
    c = "".join(f'<span class="chip">{svg(i, 28) if i else ""}{esc(t)}</span>' for t, i in zip(sp["chips"], icons))
    return f'<div class="chips" style="bottom:{bottom}px;left:{left}px;width:{width}px">{c}</div>'

def shield_html(sp, left=None, bottom=None, right=None, top=None):
    if not sp.get("shield"): return ""
    pos = ";".join(f"{k}:{v}px" for k, v in [("left", left), ("bottom", bottom), ("right", right), ("top", top)] if v is not None)
    return (f'<div class="shield" style="{pos}">'
            f'<svg width="42" height="42" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z"/><path d="M8.5 12l2.5 2.5 4.5-5" stroke="{VERDE}"/></svg></div>')

def item_html(it, i, num, column=False):
    if num: mark, cls = str(i), "ic num"
    else:
        ic = it.get("icon", "check")
        mark, cls = svg(ic, 34, VERDE if ic == "check" else "#fff", 2.4), "ic"
    desc = f'<span>{esc(it["d"])}</span>' if it.get("d") else ""
    st = ' style="flex:1;flex-direction:column;align-items:center;text-align:center;gap:14px"' if column else ""
    return f'<div class="it"{st}><div class="{cls}">{mark}</div><div><b>{esc(it["t"])}</b>{desc}</div></div>'

def items_html(sp, column=False):
    num = sp.get("style") == "num"
    return "".join(item_html(it, i, num, column) for i, it in enumerate(sp.get("items", []), 1))

def markers_html(sp):
    return "".join(f'<span class="mk" style="left:{m["x"]*100:.1f}%;top:{m["y"]*100:.1f}%">{m.get("n", "")}</span>' for m in sp.get("markers", []))

def product_box(im, left, top, bw, bh, extra="", rad="0"):
    """Coloca a foto (já preparada) centrada numa caixa; devolve html e a geometria (x, y, w, h) no quadro."""
    iw, ih = im.size
    sc = min(bw / iw, bh / ih); dw, dh = int(iw * sc), int(ih * sc)
    x, y = left + (bw - dw) // 2, top + (bh - dh) // 2
    h = (f'<div style="position:absolute;left:{x}px;top:{y}px;width:{dw}px;height:{dh}px">'
         f'<img src="img.png" style="width:100%;height:100%;display:block;border-radius:{rad}">{extra}</div>')
    return h, (x, y, dw, dh)

def zooms_html(sp, im, work, geom):
    """Lupas circulares: ampliam o ponto (x,y) da foto, ficam em `at` (fração do quadro) e ligam-se ao ponto por linha fina."""
    x0, y0, dw, dh = geom
    out, lines = "", ""
    for k, z in enumerate(sp.get("zooms", [])):
        d = z.get("d", 236); zf = z.get("zoom", 2.4)
        # recorte da foto em volta do ponto, em px da foto real
        iw, ih = im.size
        cx, cy = z["x"] * iw, z["y"] * ih
        half = (d / 2) / (dw / iw) / zf  # metade do recorte em px da foto
        box = (int(cx - half), int(cy - half), int(cx + half), int(cy + half))
        crop = Image.new("RGB", (box[2] - box[0], box[3] - box[1]), "white")
        crop.paste(im.crop((max(box[0], 0), max(box[1], 0), min(box[2], iw), min(box[3], ih))), (max(0, -box[0]), max(0, -box[1])))
        crop = crop.resize((d * SCALE, d * SCALE), Image.LANCZOS)
        save(crop, work / f"z{k}.png")
        ax, ay = z["at"][0] * S, z["at"][1] * S  # centro da lupa no quadro
        px, py = x0 + z["x"] * dw, y0 + z["y"] * dh  # ponto na foto, no quadro
        ang = math.atan2(py - ay, px - ax)
        sx, sy = ax + math.cos(ang) * (d / 2 + 3), ay + math.sin(ang) * (d / 2 + 3)
        lines += (f'<line x1="{sx:.0f}" y1="{sy:.0f}" x2="{px:.0f}" y2="{py:.0f}" stroke="{ROXO}" stroke-width="3" stroke-linecap="round"/>'
                  f'<circle cx="{px:.0f}" cy="{py:.0f}" r="9" fill="{ROXO}" stroke="{VERDE}" stroke-width="3"/>')
        # número preso à borda da lupa, do lado oposto à linha
        up = py >= ay - 60  # número em cima, salvo quando a linha sobe
        nx, ny = ax, (ay - (d / 2 - 4)) if up else (ay + (d / 2 - 4))
        out += (f'<div class="zoom" style="left:{ax - d/2:.0f}px;top:{ay - d/2:.0f}px;width:{d}px;height:{d}px">'
                f'<img src="z{k}.png" style="left:0;top:0;width:{d}px;height:{d}px"></div>'
                f'<div class="zn" style="left:{nx - 26:.0f}px;top:{ny - 26:.0f}px">{z.get("n", k + 1)}</div>')
    svg_lines = f'<svg style="position:absolute;inset:0;z-index:2" width="{S}" height="{S}">{lines}</svg>' if lines else ""
    return svg_lines + out

def build(sp, work, base):
    lay = sp["layout"]; src = source(base, sp["img"])
    im = load(src, sp.get("crop"))
    w = bool(sp.get("white"))
    two = bool(sp.get("t1") and sp.get("t2"))

    if lay == "capa":
        save(whiten_trim(im, trim=False), work / "img.png")
        body = '<img src="img.png" style="position:absolute;left:62px;top:62px;width:900px;height:900px;object-fit:contain">'

    elif lay == "hero":  # foto inteira, título em cima sobre degradê branco
        save(fit_box(im, S, S), work / "img.png")
        left = sp.get("align") == "left"
        sub = ""
        if sp.get("sub"):
            ic = svg(sp["icon"], 64, sw=1.6) if sp.get("icon") else ""
            pos = f'left:60px;width:620px;justify-content:flex-start' if left else f'left:0;width:{S}px;justify-content:center'
            sub = (f'<div style="position:absolute;top:{300 if two else 210}px;{pos};display:flex;'
                   f'align-items:center;gap:20px">{ic}<p class="sub" style="margin:0;text-align:left">{esc(sp["sub"])}</p></div>')
        tb = title_block(sp, 70, left=60, width=620, bar=False, max_w=600) if left else title_block(sp, 70, bar=False)
        body = (f'<img src="img.png" style="position:absolute;inset:0;width:{S}px;height:{S}px;object-fit:cover">'
                f'<div style="position:absolute;left:0;top:0;width:{S}px;height:430px;background:linear-gradient(180deg,rgba(255,255,255,.92) 0%,rgba(255,255,255,.62) 62%,rgba(255,255,255,0) 100%)"></div>'
                + tb + sub + chips_html(sp, 56) + shield_html(sp, left=56, bottom=56))

    elif lay == "overlay":  # foto inteira, título embaixo sobre degradê branco (espelho do hero)
        save(fit_box(im, S, S), work / "img.png")
        sub = f'<p class="sub" style="position:absolute;bottom:62px;left:0;width:{S}px;margin:0;text-align:center">{esc(sp["sub"])}</p>' if sp.get("sub") else ""
        tt = S - 62 - (58 if sp.get("sub") else 0) - (172 if two else 90)
        body = (f'<img src="img.png" style="position:absolute;inset:0;width:{S}px;height:{S}px;object-fit:cover">'
                f'<div style="position:absolute;left:0;bottom:0;width:{S}px;height:470px;background:linear-gradient(0deg,rgba(255,255,255,.95) 0%,rgba(255,255,255,.7) 55%,rgba(255,255,255,0) 100%)"></div>'
                + title_block(sp, tt, bar=False) + sub + shield_html(sp, right=56, top=56))

    elif lay == "card":  # título em cima, foto em cartão arredondado
        sub_top = 232 if two else 150
        card_top = sub_top + (118 if sp.get("sub") else 36)
        ch = S - card_top - 50
        save(fit_box(im, 924, ch), work / "img.png")
        sub = f'<p class="sub" style="position:absolute;top:{sub_top}px;left:0;width:{S}px;margin:0;text-align:center">{esc(sp.get("sub"))}</p>' if sp.get("sub") else ""
        body = (title_block(sp, 58) + sub +
                f'<div class="card" style="left:50px;top:{card_top}px;width:924px;height:{ch}px"><img src="img.png"></div>'
                + chips_html(sp, 84) + shield_html(sp, left=78, bottom=78))

    elif lay == "split":  # metade foto (inteira na altura), metade texto alinhado à esquerda
        right = sp.get("side") == "right"
        pw = sp.get("photo_w", 520)
        save(fit_box(im, pw, S), work / "img.png")
        px = S - pw if right else 0
        tx = 56 if right else pw + 50
        tw = S - pw - 100
        t = title_block(sp, 150 if not sp.get("items") else 96, left=tx, width=tw, max_w=tw)
        y = (150 if not sp.get("items") else 96) + (172 if two else 90) + 40
        sub = ""
        if sp.get("sub"):
            ic = svg(sp["icon"], 56, sw=1.6) if sp.get("icon") else ""
            sub = (f'<div style="position:absolute;top:{y}px;left:{tx}px;width:{tw}px;display:flex;align-items:flex-start;gap:16px">'
                   f'{ic}<p class="sub" style="margin:0">{esc(sp["sub"])}</p></div>')
            y += 110
        its = f'<div class="items" style="position:absolute;left:{tx}px;top:{y}px;width:{tw}px;gap:26px">{items_html(sp)}</div>' if sp.get("items") else ""
        body = (f'<img src="img.png" style="position:absolute;left:{px}px;top:0;width:{pw}px;height:{S}px;object-fit:cover">'
                + t + sub + its + shield_html(sp, left=(px + 40), bottom=40))

    elif lay == "lista":  # foto de um lado, itens do outro
        top = 300 if two else 214
        if w: im = whiten_trim(im)
        save(im, work / "img.png")
        right = sp.get("side") == "right"
        bw, bh = 430, S - top - 60
        pb, _ = product_box(im, (S - 40 - bw) if right else 40, top, bw, bh, markers_html(sp), "0" if w else "28px")
        lx = 44 if right else 500
        body = (title_block(sp, 58) + pb +
                f'<div class="items" style="position:absolute;left:{lx}px;top:{top}px;width:480px;height:{bh}px;justify-content:center">{items_html(sp)}</div>')

    elif lay == "passos":  # foto larga em cima, itens em colunas embaixo
        top = 300 if two else 214
        if w: im = whiten_trim(im)
        save(im if w else fit_box(im, 900, 400), work / "img.png")
        bh = 400 if two else 470
        pb, _ = product_box(im if w else Image.new("RGB", (900, 400)), 62, top, 900, bh, markers_html(sp), "0" if w else "28px")
        body = (title_block(sp, 58) + pb +
                f'<div style="position:absolute;left:52px;top:{top + bh + 30}px;width:920px;display:flex;gap:28px">{items_html(sp, column=True)}</div>')

    elif lay == "detalhe":  # produto grande + lupas de zoom ligadas ao ponto + legenda numerada
        top = 232 if two else 160
        if w: im = whiten_trim(im)
        save(im, work / "img.png")
        pl, pt, pw, ph = sp.get("photo_box", [60, top, 904, 480])
        pb, geom = product_box(im, pl, pt, pw, ph, "", "0" if w else "28px")
        legend_top = sp.get("legend_top", 790)
        body = (title_block(sp, 58) + pb + zooms_html(sp, im, work, geom) +
                f'<div style="position:absolute;left:52px;top:{legend_top}px;width:920px;display:flex;gap:28px">{items_html(sp, column=True)}</div>')
    else:
        raise SystemExit(f"layout desconhecido: {lay}")
    return page(body)

def check(sp, path):
    im = Image.open(path).convert("RGB"); w, h = im.size; warns = []
    if (w, h) != (S, S): warns.append(f"tamanho {w}x{h}")
    if sp["layout"] == "capa":
        px = [im.getpixel(p) for p in [(4, 4), (w - 5, 4), (4, h - 5), (w - 5, h - 5), (w // 2, 4), (w // 2, h - 5)]]
        if any(min(c) < 250 for c in px): warns.append("fundo da capa não é branco puro nos cantos")
    if not sp.get("alt"): warns.append("sem alt text")
    elif len(sp["alt"]) > 140: warns.append(f"alt com {len(sp['alt'])} caracteres (máx. ~125)")
    return warns

def preview(out_dir, specs):
    ims = [Image.open(out_dir / sp["out"]).resize((340, 340), Image.LANCZOS) for sp in specs if (out_dir / sp["out"]).exists()]
    cols = 3; rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 350 + 10, rows * 350 + 10), "#DDDDDD")
    for i, im in enumerate(ims): sheet.paste(im, (10 + (i % cols) * 350, 10 + (i // cols) * 350))
    sheet.save(out_dir / "_preview.jpg", quality=88); return out_dir / "_preview.jpg"

def main():
    spec_path = pathlib.Path(sys.argv[1]).resolve()
    out_dir = pathlib.Path(sys.argv[sys.argv.index("--out-dir") + 1]).resolve() if "--out-dir" in sys.argv else spec_path.parent / "final"
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    out_dir.mkdir(parents=True, exist_ok=True)
    specs = json.loads(spec_path.read_text(encoding="utf-8"))
    todo = [sp for sp in specs if not only or any(f"-{n.zfill(2)}-" in sp["out"] for n in only)]
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": S, "height": S}, device_scale_factor=SCALE)
        for sp in todo:
            work = pathlib.Path(tempfile.mkdtemp())
            for ff in FONT_FILES: shutil.copy(ff, work / ff.name)
            (work / "a.html").write_text(build(sp, work, spec_path.parent), encoding="utf-8")
            pg.goto((work / "a.html").as_uri()); pg.evaluate("document.fonts.ready"); pg.evaluate(FIT_JS)
            pg.wait_for_timeout(150)
            tmp = work / "o.png"; pg.locator(".art").screenshot(path=str(tmp))
            big = Image.open(tmp).convert("RGB")
            final = big.resize((S, S), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1.0, percent=45, threshold=2))
            final.save(out_dir / sp["out"], quality=92, optimize=True)
            wn = check(sp, out_dir / sp["out"])
            print(("AVISO " + "; ".join(wn) + " -> ") if wn else "ok ", sp["out"])
        b.close()
    print("preview:", preview(out_dir, specs))

if __name__ == "__main__":
    main()
