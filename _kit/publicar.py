"""Monta o payload de imagens para o update_product da Nuvemshop a partir do spec.json.

uso: python3 _kit/publicar.py <produto>/spec.json [--sha <commit>]
Imprime o JSON da lista `images` (src com URL fixa no commit, position 1..N, alt pt_BR).
Sem --sha usa o HEAD atual do repositório (faça o push antes).
"""
import json, sys, subprocess, pathlib
spec = pathlib.Path(sys.argv[1]).resolve()
repo = spec.parents[1]
sha = sys.argv[sys.argv.index("--sha") + 1] if "--sha" in sys.argv else subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
remote = subprocess.check_output(["git", "-C", str(repo), "remote", "get-url", "origin"], text=True).strip()
owner_repo = remote.rstrip("/").removesuffix(".git").split("github.com/")[-1]
pasta = spec.parent.name
items = json.loads(spec.read_text(encoding="utf-8"))
out = [{"src": f"https://raw.githubusercontent.com/{owner_repo}/{sha}/{pasta}/{it['out']}", "position": i + 1, "alt": {"pt_BR": it["alt"]}}
       for i, it in enumerate(items)]
print(json.dumps(out, ensure_ascii=False))
