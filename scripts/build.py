#!/usr/bin/env python3
"""Gera as páginas publicadas a partir de src/ (só biblioteca padrão).

Fonte (src/): páginas em PT com a tradução EN em atributos data-en*:
  data-en           troca o texto do elemento
  data-en-html      troca o HTML interno do elemento
  data-en-<attr>    troca o atributo <attr> (aria -> aria-label, ph -> placeholder; href, lang, content, title...)
  <!--include:x-->  insere src/partials/x.html (com {{MARCADORES}} trocados por página)

Saída (raiz do repositório, o que o GitHub Pages serve):
  index.html                     /                    PT, sem nenhum data-en
  en/index.html                  /en/                 EN
  casos/<slug>/index.html        /casos/<slug>/       estudos de caso em PT
  en/cases/<slug>/index.html     /en/cases/<slug>/    estudos de caso em EN
  404.html, sitemap.xml

Cada página sai com o CSS inline (css/site.css, sem minificação perigosa) para não haver pedido
bloqueante de folha de estilo, e com todos os caminhos relativos recalculados pela profundidade.

Uso:  python3 scripts/build.py [--check]
Com --check, não escreve: sai com erro se alguma saída estiver desatualizada.
"""
import html
import json
import posixpath
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SRC = RAIZ / "src"
SITE = "https://jonasaaugusto.github.io"
VAZIOS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
ALIAS = {"aria": "aria-label", "ph": "placeholder"}
URLS = ("href", "src", "poster")

CASOS = ("f5", "iaprovale", "orquestrador")
PAGINAS = [dict(src="index.html", pt="index.html", en="en/index.html")] + [
    dict(src=f"casos/{c}.html", pt=f"casos/{c}/index.html", en=f"en/cases/{c}/index.html", caso=c) for c in CASOS
]


def relativo(valor):
    return bool(valor) and not re.match(r"^([a-z][a-z0-9+.-]*:|//|#|/|data:)", valor, re.I)


def rebase(valor, prefixo):
    """Recalcula um caminho escrito a partir da raiz para a página que está `prefixo` acima (ou em '/')."""
    m = re.match(r"^([^?#]*)([?#].*)?$", valor)
    caminho, resto = m.group(1), m.group(2) or ""
    if prefixo == "/":
        return "/" + caminho.lstrip("./") + resto
    if caminho in ("", ".", "./"):
        junto = prefixo or "./"
    else:
        junto = posixpath.normpath(prefixo + caminho)
        if caminho.endswith("/"):
            junto += "/"
    return junto + resto


class Gerador(HTMLParser):
    def __init__(self, lang, prefixo):
        super().__init__(convert_charrefs=False)
        self.lang, self.prefixo = lang, prefixo
        self.saida = []
        self.pular = None  # [tag, profundidade, modo] enquanto o conteúdo é substituído

    def tag(self, tag, attrs, fecha=False):
        en = {k[8:]: v for k, v in attrs if k.startswith("data-en-") and k != "data-en-html"}
        trocar = self.lang == "en"
        novos = []
        for k, v in attrs:
            if k == "data-en" or k.startswith("data-en-"):
                continue
            for a, b in ALIAS.items():
                if trocar and k == b and a in en:
                    v = en[a]
            if trocar and k in en:
                v = en[k]
            elif k in URLS and v is not None and relativo(v):
                v = rebase(v, self.prefixo)
            novos.append((k, v))
        if trocar:
            presentes = {k for k, _ in novos}
            for a, v in en.items():
                alvo = ALIAS.get(a, a)
                if alvo not in presentes:
                    novos.append((alvo, v))
        if tag == "html":
            novos = [(k, v) for k, v in novos if k not in ("lang", "data-base")]
            novos = [("lang", "en" if trocar else "pt-BR"), ("data-base", self.prefixo if self.prefixo != "/" else "")] + novos
        partes = [k if v is None else f'{k}="{html.escape(v, quote=True)}"' for k, v in novos]
        return "<" + tag + ("" if not partes else " " + " ".join(partes)) + ("/>" if fecha else ">")

    def handle_starttag(self, tag, attrs):
        if self.pular:
            if tag == self.pular[0]:
                self.pular[1] += 1
            if tag not in VAZIOS and self.pular[2] == "texto":
                raise SystemExit(f"data-en em <{self.pular[0]}> com filho <{tag}>: use data-en-html")
            return
        d = dict(attrs)
        self.saida.append(self.tag(tag, attrs))
        if tag in VAZIOS or self.lang != "en":
            return
        if "data-en" in d:
            self.saida.append(html.escape(d["data-en"], quote=False))
            self.pular = [tag, 1, "texto"]
        elif "data-en-html" in d:
            self.saida.append(d["data-en-html"])
            self.pular = [tag, 1, "html"]

    def handle_startendtag(self, tag, attrs):
        if not self.pular:
            self.saida.append(self.tag(tag, attrs, fecha=True))

    def handle_endtag(self, tag):
        if self.pular:
            if tag == self.pular[0]:
                self.pular[1] -= 1
                if self.pular[1] == 0:
                    self.pular = None
                    self.saida.append(f"</{tag}>")
            return
        self.saida.append(f"</{tag}>")

    def _raw(self, s):
        if not self.pular:
            self.saida.append(s)

    def handle_data(self, data): self._raw(data)
    def handle_entityref(self, name): self._raw(f"&{name};")
    def handle_charref(self, name): self._raw(f"&#{name};")
    def handle_comment(self, data): self._raw(f"<!--{data}-->")
    def handle_decl(self, decl): self._raw(f"<!{decl}>")
    def handle_pi(self, data): self._raw(f"<?{data}>")


def css_inline(prefixo):
    css = (RAIZ / "css" / "site.css").read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,])\s*", r"\1", css)
    css = css.replace("url('../assets/", f"url('{prefixo if prefixo != '/' else '/'}assets/")
    return "<style>" + css.strip() + "</style>"


def jsonld(lang):
    pt = lang != "en"
    dados = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": "Jonas Augusto",
        "url": SITE + ("/" if pt else "/en/"),
        "image": SITE + "/assets/img/og-image.png",
        "jobTitle": "Engenheiro de software" if pt else "Software engineer",
        "description": ("Engenheiro de software (formação em dez/2026). Construo e opero APIs, automações e integrações de IA em produção, com backend em Python e C#."
                        if pt else "Software engineer (graduating Dec 2026). I build and run APIs, automations and AI integrations in production, with a Python and C# backend."),
        "worksFor": [
            {"@type": "Organization", "name": "Augustus AI Solutions"},
            {"@type": "Organization", "name": "F5 Tecnologia"},
        ],
        "alumniOf": {"@type": "CollegeOrUniversity", "name": "Universidade Estácio de Sá"},
        "address": {"@type": "PostalAddress", "addressLocality": "Juiz de Fora", "addressRegion": "MG", "addressCountry": "BR"},
        "knowsAbout": ["Python", "C#", ".NET", "FastAPI", "PostgreSQL", "Docker", "Linux", "Backend", "Automation", "AI agents"],
        "sameAs": ["https://github.com/JonasaAugusto", "https://www.linkedin.com/in/jonasaaugusto"],
    }
    return '<script type="application/ld+json">' + json.dumps(dados, ensure_ascii=False, separators=(",", ":")) + "</script>"


def incluir(texto, pagina):
    """Resolve <!--include:x--> e os {{MARCADORES}} que dependem da página."""
    pt_dir = posixpath.dirname(pagina["pt"]) or "."
    en_dir = posixpath.dirname(pagina["en"]) or "."
    marcas = {
        "HOME_EN": posixpath.relpath("en", en_dir) + "/",
        "CV_EN": posixpath.relpath("JonasAugusto_cv_en.pdf", en_dir),
        "LANG_PT": pagina["en"].rsplit("index.html", 1)[0],
        "LANG_EN": posixpath.relpath(pt_dir, en_dir) + "/",
    }

    def troca(m):
        corpo = (SRC / "partials" / f"{m.group(1)}.html").read_text(encoding="utf-8")
        for k, v in marcas.items():
            corpo = corpo.replace("{{" + k + "}}", v)
        return corpo.rstrip("\n")
    return re.sub(r"<!--include:([a-z0-9-]+)-->", troca, texto)


def gerar_pagina(pagina, lang):
    saida = pagina[lang]
    prefixo = "../" * saida.count("/")
    texto = incluir((SRC / pagina["src"]).read_text(encoding="utf-8"), pagina)
    g = Gerador(lang, prefixo)
    g.feed(texto)
    g.close()
    out = "".join(g.saida)
    out = re.sub(r'<link rel="stylesheet" href="[^"]*css/site\.css">', lambda m: css_inline(prefixo), out)
    out = out.replace("<!--jsonld-->", jsonld(lang))
    if lang != "en" and re.search(r"\sdata-en", out):
        raise SystemExit(f"{saida}: sobrou data-en* na versão PT")
    return out


def gerar_404():
    texto = (SRC / "404.html").read_text(encoding="utf-8")
    g = Gerador("pt", "/")
    g.feed(texto)
    g.close()
    out = "".join(g.saida)
    return re.sub(r'<link rel="stylesheet" href="[^"]*css/site\.css">', lambda m: css_inline("/"), out)


def gerar_sitemap():
    linhas = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for p in PAGINAS:
        url = {lg: SITE + "/" + p[lg].replace("index.html", "") for lg in ("pt", "en")}
        for lg in ("pt", "en"):
            linhas += ["  <url>", f"    <loc>{url[lg]}</loc>",
                       f'    <xhtml:link rel="alternate" hreflang="pt-BR" href="{url["pt"]}"/>',
                       f'    <xhtml:link rel="alternate" hreflang="en" href="{url["en"]}"/>',
                       f'    <xhtml:link rel="alternate" hreflang="x-default" href="{url["pt"]}"/>', "  </url>"]
    linhas.append("</urlset>")
    return "\n".join(linhas) + "\n"


def saidas():
    s = {}
    for p in PAGINAS:
        for lg in ("pt", "en"):
            s[p[lg]] = gerar_pagina(p, lg)
    if (SRC / "404.html").exists():
        s["404.html"] = gerar_404()
    s["sitemap.xml"] = gerar_sitemap()
    return s


if __name__ == "__main__":
    todas = saidas()
    if "--check" in sys.argv:
        velhas = [c for c, t in todas.items() if not (RAIZ / c).exists() or (RAIZ / c).read_text(encoding="utf-8") != t]
        if velhas:
            sys.exit("desatualizado: " + ", ".join(velhas) + " (rode python3 scripts/build.py)")
        print(f"{len(todas)} arquivos em dia")
    else:
        for caminho, texto in todas.items():
            alvo = RAIZ / caminho
            alvo.parent.mkdir(parents=True, exist_ok=True)
            alvo.write_text(texto, encoding="utf-8", newline="\n")
            print(f"gerado {caminho} ({len(texto.encode('utf-8'))} bytes)")
