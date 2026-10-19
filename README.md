# ZeloKids – imagens de produtos

Imagens finais dos produtos da loja ZeloKids, uma pasta por produto. A Nuvemshop baixa as fotos daqui pelo link `raw.githubusercontent.com`.

- `<produto>/` — 9 JPGs 1024×1024 + `spec.json` (textos, layout e alt text de cada imagem) + `_fontes/` (fotos e cenários usados).
- `_kit/` — `render.py` (gera as artes a partir do `spec.json`), `gerar_cena.py` (cenários com Gemini; chave em `GEMINI_API_KEY` ou no `.env` da pasta ZeloKids_Geral), `sistema-visual.md` (regras da marca) e a fonte Lexend.

Gerar as artes de um produto: `python3 _kit/render.py <produto>/spec.json --out-dir <produto>`
