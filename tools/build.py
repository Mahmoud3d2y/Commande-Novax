"""Injecte data/catalogue.json dans index.html (entre les marqueurs CATALOGUE)."""
import json, os, re
root = os.path.join(os.path.dirname(__file__), "..")
cat = json.load(open(os.path.join(root, "data", "catalogue.json"), encoding="utf-8"))
p = os.path.join(root, "index.html")
html = open(p, encoding="utf-8").read()
js = "window.CATALOGUE = " + json.dumps(cat, ensure_ascii=False, separators=(",", ":")) + ";"
html = re.sub(r"/\*CATALOGUE:START\*/.*?/\*CATALOGUE:END\*/",
              lambda m: "/*CATALOGUE:START*/" + js + "/*CATALOGUE:END*/", html, flags=re.S)
open(p, "w", encoding="utf-8").write(html)
print("index.html mis à jour")
