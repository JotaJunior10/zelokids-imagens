"""Gera/edita uma imagem 1:1 com o Gemini (padrão ZeloKids).
uso: gerar_cena.py --prompt arquivo.txt --out saida.png [--ref foto.png] [--pad 0.64] [--model gemini-3.1-flash-image]
--ref  : foto do produto (o produto deve ser preservado). Sem --ref = gera só cenário.
--pad  : reduz o produto para essa fração do quadro, no centro-baixo, e deixa o resto vazio para a IA completar.
A chave vem de GEMINI_API_KEY no ambiente ou do arquivo .env da pasta ZeloKids_Geral (nunca é impressa)."""
import argparse, os, io, json, base64, urllib.request, urllib.error, pathlib, sys
ap = argparse.ArgumentParser()
ap.add_argument("--prompt", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--ref"); ap.add_argument("--pad", type=float); ap.add_argument("--model", default="gemini-3.1-flash-image")
a = ap.parse_args()
key = os.environ.get("GEMINI_API_KEY")
if not key:
    root = pathlib.Path(__file__).resolve().parents[2]
    key = next(l.split("=",1)[1].strip().strip('"') for l in open(root/".env", encoding="utf-8") if l.startswith("GEMINI_API_KEY="))
parts = []
if a.ref:
    from PIL import Image
    im = Image.open(a.ref).convert("RGB")
    if a.pad:
        W = 1024; s = int(W*a.pad)
        im.thumbnail((s, s), Image.LANCZOS)
        c = Image.new("RGB", (W, W), (240,240,240)); c.paste(im, ((W-im.width)//2, W-im.height-10)); im = c
    buf = io.BytesIO(); im.save(buf, "PNG")
    parts.append({"inline_data":{"mime_type":"image/png","data":base64.b64encode(buf.getvalue()).decode()}})
parts.append({"text": open(a.prompt, encoding="utf-8").read()})
body = {"contents":[{"parts":parts}], "generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":"1:1"}}}
req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{a.model}:generateContent",
      data=json.dumps(body).encode(), headers={"Content-Type":"application/json","x-goog-api-key":key})
try: d = json.load(urllib.request.urlopen(req, timeout=170))
except urllib.error.HTTPError as e: print("ERRO", e.code, e.read().decode()[:600]); sys.exit(1)
for c in d.get("candidates",[]):
    for p in c.get("content",{}).get("parts",[]):
        b = p.get("inline_data") or p.get("inlineData")
        if b: open(a.out,"wb").write(base64.b64decode(b["data"])); print("OK", a.out); sys.exit(0)
print("SEM IMAGEM", json.dumps(d)[:600]); sys.exit(2)
