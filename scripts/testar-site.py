#!/usr/bin/env python3
"""Testes estruturais do portfólio (só biblioteca padrão): python3 scripts/testar-site.py

- as saídas publicadas estão em dia com src/ (scripts/build.py --check);
- cada página PT tem a gêmea EN com os mesmos ids, landmarks, headings e links;
- PT e EN não têm restos de data-en*, têm lang/canonical/hreflang corretos e caminhos que resolvem;
- um h1 por página, headings sem pulo de nível, sem Claude/Codex fora do projeto Orchestrator;
- o alternador de idioma é um link comum (funciona sem JavaScript);
- sitemap, robots e 404 existem; todo link interno (incluindo âncoras) resolve.
"""
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
falhas = []
CASOS = ("f5", "iaprovale", "orquestrador")
PARES = [("index.html", "en/index.html")] + [(f"casos/{c}/index.html", f"en/cases/{c}/index.html") for c in CASOS]
URL_PT = {"index.html": "", **{f"casos/{c}/index.html": f"casos/{c}/" for c in CASOS}}
URL_EN = {"en/index.html": "en/", **{f"en/cases/{c}/index.html": f"en/cases/{c}/" for c in CASOS}}


def checa(ok, msg):
    if not ok:
        falhas.append(msg)
    print(("ok    " if ok else "FALHA ") + msg)


class Mapa(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.heads, self.landmarks, self.links, self.srcs, self.dialogs = [], [], [], [], [], []
        self.attrs_en = 0
        self.form = 0
        self.lang = None
        self.lang_btn = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if a.get("id"):
            self.ids.append(a["id"])
        if a.get("id") == "lang-btn":
            self.lang_btn = a.get("href")
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


def ler(p):
    return (RAIZ / p).read_text(encoding="utf-8")


def mapa(p):
    m = Mapa()
    m.feed(ler(p))
    return m


build = subprocess.run([sys.executable, str(RAIZ / "scripts/build.py"), "--check"], capture_output=True, text=True)
checa(build.returncode == 0, "saídas em dia com src/ " + (build.stderr.strip() or build.stdout.strip()))
for extra in ("sitemap.xml", "robots.txt", "404.html"):
    checa((RAIZ / extra).exists(), f"{extra} existe")

orq_re = [r'<article id="proj-orquestrador".*?</article>',
          r'<li>\s*<a class="pcard" href="#proj-orquestrador">.*?</li>',
          r'<script.*?</script>']

for ppt, pen in PARES:
    pt, en = mapa(ppt), mapa(pen)
    n = f"[{ppt}]"
    checa(pt.ids == en.ids, f"{n} PT e EN têm os mesmos ids, na mesma ordem")
    checa(pt.heads == en.heads, f"{n} mesma sequência de headings")
    checa(pt.landmarks == en.landmarks, f"{n} mesmos landmarks")
    checa(pt.dialogs == en.dialogs, f"{n} mesmos diálogos")
    checa(pt.form == en.form == 0, f"{n} sem formulário")
    checa(len(pt.links) == len(en.links), f"{n} mesmo número de links")
    checa(pt.attrs_en == 0 and en.attrs_en == 0, f"{n} sem atributos data-en* sobrando")
    checa(pt.lang == "pt-BR" and en.lang == "en", f"{n} html lang pt-BR / en")
    for nome, m in (("PT", pt), ("EN", en)):
        checa(m.heads.count(1) == 1, f"{n} {nome}: um único h1")
        pulos = [(a, b) for a, b in zip(m.heads, m.heads[1:]) if b - a > 1]
        checa(not pulos, f"{n} {nome}: headings sem pulo de nível {pulos[:3]}")
    tpt, ten = ler(ppt), ler(pen)
    cpt, cen = "https://jonasaaugusto.github.io/" + URL_PT[ppt], "https://jonasaaugusto.github.io/" + URL_EN[pen]
    checa(f'rel="canonical" href="{cpt}"' in tpt, f"{n} PT: canonical {cpt}")
    checa(f'rel="canonical" href="{cen}"' in ten, f"{n} EN: canonical {cen}")
    for h in ('hreflang="pt-BR"', 'hreflang="en"', 'hreflang="x-default"'):
        checa(h in tpt and h in ten, f"{n} hreflang {h}")
    checa(pt.lang_btn is not None and en.lang_btn is not None, f"{n} alternador de idioma é um link (sem JS)")
    # caminhos relativos resolvem a partir da pasta de cada saída; âncoras existem na página de destino
    for pasta, m in ((Path(ppt).parent, pt), (Path(pen).parent, en)):
        quebrados = []
        for ref in m.srcs + m.links:
            base = ref.split("#")[0].split("?")[0]
            if not base or re.match(r"^([a-z][a-z0-9+.-]*:|//)", base, re.I):
                continue
            alvo = (RAIZ / pasta / base).resolve() if not base.startswith("/") else (RAIZ / base.lstrip("/")).resolve()
            if alvo.is_dir():
                alvo = alvo / "index.html"
            if not alvo.exists():
                quebrados.append(ref)
            elif "#" in ref and alvo.suffix == ".html":
                frag = ref.split("#", 1)[1]
                if frag and f'id="{frag}"' not in alvo.read_text(encoding="utf-8"):
                    quebrados.append(ref)
        checa(not quebrados, f"{n} {pasta.as_posix()}: links e âncoras internos existem {quebrados[:5]}")
    # nomes de ferramentas: só dentro do projeto Orchestrator
    if "orquestrador" not in ppt:
        for nome, txt in (("PT", tpt), ("EN", ten)):
            corpo = txt
            for r in orq_re:
                corpo = re.sub(r, "", corpo, flags=re.S)
            corpo = re.sub(r'<link[^>]*>|<meta[^>]*>', "", corpo)
            checa(not re.search(r"claude|codex|anthropic", corpo, re.I), f"{n} {nome}: Claude/Codex só dentro do projeto Orchestrator")

for cv in ("cv.html", "cv.en.html"):
    checa(not re.search(r"claude|codex|anthropic", ler(cv), re.I), f"{cv} sem Claude/Codex")
    checa(not re.search(r"\bCEO\b", ler(cv)), f"{cv} sem o título 'CEO'")
site = ler("index.html") + ler("en/index.html")
checa(not re.search(r"\bCEO\b|vibe coding", site), "site sem 'CEO' nem 'vibe coding'")
sys.exit(1 if falhas else 0)
