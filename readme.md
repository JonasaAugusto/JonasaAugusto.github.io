# Portfólio Jonas Augusto

Portfólio pessoal publicado em [jonasaaugusto.github.io](https://jonasaaugusto.github.io), em português (`/`) e inglês (`/en/`).

## Stack

- **HTML, CSS e JavaScript puros**, sem framework e sem scripts de terceiros. Um gerador em Python (só biblioteca padrão) monta as páginas publicadas
- **Geist e Geist Mono** (variáveis, self-hosted em `assets/fonts/`); a mono aparece só em medidas, datas e stack

## Estrutura

- `src/`: **fonte editável**. `src/index.html` (página única em PT, com a tradução EN em atributos `data-en*`), `src/casos/*.html` (estudos de caso), `src/partials/` (cabeçalho e rodapé das páginas de caso) e `src/404.html`
- `scripts/build.py`: gera as páginas publicadas a partir de `src/`. Rode `python3 scripts/build.py` a cada mudança (e `--check` para conferir). Saída: `index.html`, `en/index.html`, `casos/<caso>/`, `en/cases/<caso>/`, `404.html` e `sitemap.xml`, com o CSS inline e os caminhos recalculados. **Não edite esses arquivos à mão.**
- `scripts/testar-site.py`: testes estruturais (saídas em dia, PT e EN com os mesmos blocos, headings, links e âncoras internas, canonical e hreflang, sem "CEO" nem Claude/Codex fora do Orchestrator)
- `robots.txt`, `sitemap.xml`, JSON-LD (Person) e `404.html` para SEO e navegação
- `css/site.css`: tokens (temas claro e escuro, escala de tipo, espaçamento) e todos os estilos; é embutido nas páginas pelo build
- `js/site.js`: tema, menu móvel, diálogo do CV, animações. O idioma não depende de JS: o alternador é um link comum
- `cv.html` e `cv.en.html`: fonte do currículo; `JonasAugusto_cv_m.pdf` e `JonasAugusto_cv_en.pdf` são os PDFs de 1 página
- `docs/`: estudo de caso da F5 em Markdown (PT e EN)

## Decisões

- **Monocromático editorial.** Preto, branco e cinzas, com o amarelo do banner só no ponto de status e na seleção de texto. A tipografia faz o trabalho.
- **Tema claro e escuro.** Segue o sistema na primeira visita e guarda a escolha em `localStorage`; o script de tema roda no `<head>` para não piscar.
- **Leitura em 30 a 60 segundos.** O topo traz uma frase, os botões de contato, três números com antes e depois (cada um com link para a fonte) e os três projetos em destaque. Os estudos de caso têm página própria, com URL compartilhável; os outros projetos ficam num `<details>` fechado.
- **Sem movimento decorativo.** Só a troca de tema usa View Transitions (desligada com `prefers-reduced-motion`). Nada fica escondido se o script falhar.
- **Repositórios privados sem link.** AugustusApp e o Conector WhatsApp aparecem sem link de código.

## Hospedagem

GitHub Pages serve os arquivos gerados que estão no repositório (o build roda localmente e o resultado é versionado).
