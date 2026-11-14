#!/usr/bin/env python3
"""Gera en/index.html (versão estática em inglês) a partir de index.html.

Os textos em inglês já vivem no próprio HTML, em atributos data-en*:
  data-en           troca o texto do elemento
  data-en-html      troca o HTML interno do elemento
  data-en-<attr>    troca o atributo <attr> (aria -> aria-label, ph -> placeholder; href, lang, content, title...)

Só biblioteca padrão. Uso:  python3 scripts/gerar-en.py [--check]
Com --check, não escreve: sai com erro se en/index.html estiver desatualizado.
"""
import html
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEM = RAIZ / "index.html"
DESTINO = RAIZ / "en" / "index.html"
VAZIOS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
ALIAS = {"aria": "aria-label", "ph": "placeholder"}
URLS = ("href", "src", "poster")


def relativo(valor: str) -> bool:
    return bool(valor) and not re.match(r"^([a-z][a-z0-9+.-]*:|//|#|/)", valor, re.I)


class Gerador(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.saida = []
        self.pular = None  # [tag, profundidade, modo] enquanto o conteúdo é substituído

    # ----- montagem de tags -----
    def tag(self, tag, attrs, fecha=False):
        en = {k[8:]: v for k, v in attrs if k.startswith("data-en-") and k != "data-en-html"}
        novos = []
        for k, v in attrs:
            if k == "data-en" or k.startswith("data-en-"):
                continue
            alvo = k
            for a, b in ALIAS.items():
                if k == b and a in en:
                    v = en[a]
            if k in en:
                v = en[k]
            elif k in URLS and v is not None and relativo(v):
                v = "../" + v
            novos.append((alvo, v))
        presentes = {k for k, _ in novos}
        for a, v in en.items():
            alvo = ALIAS.get(a, a)
            if alvo not in presentes:
                novos.append((alvo, v))
        if tag == "html":
            novos = [(k, v) for k, v in novos if k not in ("lang", "data-base")] + [("lang", "en"), ("data-base", "../")]
            novos.sort(key=lambda kv: kv[0] != "lang")
        partes = []
        for k, v in novos:
            partes.append(k if v is None else f'{k}="{html.escape(v, quote=True)}"')
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
        if tag in VAZIOS:
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

    # ----- o resto passa como veio -----
    def _raw(self, s):
        if not self.pular:
            self.saida.append(s)

    def handle_data(self, data): self._raw(data)
    def handle_entityref(self, name): self._raw(f"&{name};")
    def handle_charref(self, name): self._raw(f"&#{name};")
    def handle_comment(self, data): self._raw(f"<!--{data}-->")
    def handle_decl(self, decl): self._raw(f"<!{decl}>")
    def handle_pi(self, data): self._raw(f"<?{data}>")


def gerar() -> str:
    g = Gerador()
    g.feed(ORIGEM.read_text(encoding="utf-8"))
    g.close()
    return "".join(g.saida)


if __name__ == "__main__":
    texto = gerar()
    if "--check" in sys.argv:
        atual = DESTINO.read_text(encoding="utf-8") if DESTINO.exists() else ""
        if atual != texto:
            sys.exit("en/index.html está desatualizado: rode python3 scripts/gerar-en.py")
        print("en/index.html está em dia")
    else:
        DESTINO.parent.mkdir(exist_ok=True)
        DESTINO.write_text(texto, encoding="utf-8")
        print(f"gerado {DESTINO.relative_to(RAIZ)} ({len(texto)} bytes)")
