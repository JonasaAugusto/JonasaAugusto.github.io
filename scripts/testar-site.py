#!/usr/bin/env python3
"""Testes estruturais do portfólio (só biblioteca padrão): python3 scripts/testar-site.py

- en/index.html está em dia com index.html (gerado por scripts/gerar-en.py);
- PT e EN têm os mesmos blocos (ids, landmarks, headings, links, diálogos, formulário);
- EN não tem restos de data-en*, tem lang/canonical/hreflang corretos e caminhos que resolvem;
- um h1 por página, headings sem pulo de nível, sem Claude/Codex fora do projeto Orchestrator;
- o alternador de idioma é um link comum (funciona sem JavaScript).
"""
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
falhas = []


def checa(ok, msg):
    if not ok:
        falhas.append(msg)
    print(("ok    " if ok else "FALHA ") + msg)


class Mapa(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.heads, self.landmarks, self.links, self.srcs, self.dialogs = [], [], [], [], [], []
        self.attrs_en = 0
        self.stack = []
        self.h1 = 0
        self.form = 0
        self.lang = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if a.get("id"):
            self.ids.append(a["id"])
        if any(k.startswith("data-en") for k in a):
            self.attrs_en += 1
        if tag in ("h1", "h2", "h3", "h4"):
            self.heads.append(int(tag[1]))
        if tag in ("main", "nav", "header", "footer"):
            self.landmarks.append(tag)
        if tag == "dialog":
            self.dialogs.append(a.get("id"))
        if tag == "form":
            self.form += 1
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        for k in ("src", "href"):
            if tag in ("link", "script", "img") and a.get(k):
                self.srcs.append(a[k])


def le(p):
    m = Mapa()
    m.feed((RAIZ / p).read_text(encoding="utf-8"))
    return m


pt, en = le("index.html"), le("en/index.html")

atual = subprocess.run([sys.executable, str(RAIZ / "scripts/gerar-en.py"), "--check"], capture_output=True, text=True)
checa(atual.returncode == 0, "en/index.html está em dia com index.html")
checa(pt.ids == en.ids, "PT e EN têm os mesmos ids, na mesma ordem")
checa(pt.heads == en.heads, "PT e EN têm a mesma sequência de headings")
checa(pt.landmarks == en.landmarks, "PT e EN têm os mesmos landmarks")
checa(pt.dialogs == en.dialogs, "PT e EN têm os mesmos diálogos")
checa(pt.form == en.form == 1, "PT e EN têm o formulário de contato")
checa(len(pt.links) == len(en.links), "PT e EN têm o mesmo número de links")
checa(en.attrs_en == 0, "EN não tem atributos data-en* sobrando")
checa(pt.lang == "pt-BR" and en.lang == "en", "html lang: pt-BR em / e en em /en/")
for nome, m in (("PT", pt), ("EN", en)):
    checa(m.heads.count(1) == 1, f"{nome}: um único h1")
    pulos = [(a, b) for a, b in zip(m.heads, m.heads[1:]) if b - a > 1]
    checa(not pulos, f"{nome}: headings sem pulo de nível {pulos[:3]}")
en_txt = (RAIZ / "en/index.html").read_text(encoding="utf-8")
pt_txt = (RAIZ / "index.html").read_text(encoding="utf-8")
checa('rel="canonical" href="https://jonasaaugusto.github.io/en/"' in en_txt, "EN: canonical aponta para /en/")
checa('rel="canonical" href="https://jonasaaugusto.github.io/"' in pt_txt, "PT: canonical aponta para /")
for h in ('hreflang="pt-BR"', 'hreflang="en"', 'hreflang="x-default"'):
    checa(h in pt_txt and h in en_txt, f"hreflang {h} nas duas páginas")
checa('id="lang-btn" href="en/"' in pt_txt and 'id="lang-btn" href="../"' in en_txt, "alternador de idioma é um link (sem JS)")
# caminhos de EN resolvem a partir de /en/
quebrados = []
for ref in en.srcs + [l for l in en.links]:
    ref = ref.split("#")[0].split("?")[0]
    if not ref or re.match(r"^([a-z][a-z0-9+.-]*:|//)", ref, re.I):
        continue
    if not (RAIZ / "en" / ref).resolve().exists():
        quebrados.append(ref)
checa(not quebrados, f"EN: caminhos relativos existem {quebrados[:5]}")
# nomes de ferramentas: só dentro do projeto Orchestrator (card, artigo e diálogo)
fora = []
for nome, txt in (("PT", pt_txt), ("EN", en_txt)):
    corpo = re.sub(r'<dialog id="dlg-orq".*?</dialog>', "", txt, flags=re.S)
    corpo = re.sub(r'<article id="proj-orquestrador".*?</article>', "", corpo, flags=re.S)
    corpo = re.sub(r'<li>\s*<a class="pcard" href="#proj-orquestrador">.*?</li>', "", corpo, flags=re.S)
    corpo = re.sub(r'<script.*?</script>', "", corpo, flags=re.S)
    if re.search(r"claude|codex|anthropic", corpo, re.I):
        fora.append(nome)
checa(not fora, f"Claude/Codex só dentro do projeto Orchestrator {fora}")
for cv in ("cv.html", "cv.en.html"):
    checa(not re.search(r"claude|codex|anthropic", (RAIZ / cv).read_text(encoding="utf-8"), re.I), f"{cv} sem Claude/Codex")
sys.exit(1 if falhas else 0)
