# Portfólio Jonas Augusto

Portfólio pessoal publicado em [jonasaaugusto.github.io](https://jonasaaugusto.github.io), em português (`/`) e inglês (`/en/`).

## Stack

- **HTML, CSS e JavaScript puros**, sem framework, sem build e sem scripts de terceiros
- **Geist e Geist Mono** (variáveis, self-hosted em `assets/fonts/`); a mono aparece só em medidas, datas e stack
- **Formspark** recebe o formulário de contato (só o `action` do formulário, nenhum script externo)

## Estrutura

- `index.html`: página única em PT; a tradução EN fica em atributos `data-en*` (fonte dos textos em inglês)
- `en/index.html`: versão estática em inglês, **gerada** por `python3 scripts/gerar-en.py` a partir do `index.html` (rode de novo a cada mudança de texto)
- `scripts/testar-site.py`: testes estruturais (PT e EN com os mesmos blocos, `/en/` em dia, headings, links, caminhos)
- `css/site.css`: tokens (cores dos temas claro e escuro, escala de tipo, espaçamento) e todos os estilos
- `js/site.js`: tema, menu móvel, diálogos do CV e dos estudos de caso e o formulário. O idioma não depende de JS: o alternador é um link entre `/` e `/en/`
- `cv.html` e `cv.en.html`: fonte do currículo (imprimir em PDF para atualizar); `JonasAugusto_cv_m.pdf` e `JonasAugusto_cv_en.pdf` são os PDFs de 1 página
- `docs/`: estudo de caso da F5 em Markdown (PT e EN)

## Decisões

- **Monocromático editorial.** Preto, branco e cinzas, com o amarelo do banner só no ponto de status e na seleção de texto. A tipografia faz o trabalho.
- **Tema claro e escuro.** Segue o sistema na primeira visita e guarda a escolha em `localStorage`; o script de tema roda no `<head>` para não piscar.
- **Leitura em 30 a 60 segundos.** O topo traz uma frase, os botões de contato, três números com antes e depois (cada um com link para a fonte) e os três projetos em destaque. Os outros projetos ficam num `<details>` fechado.
- **Sem movimento decorativo.** Só a troca de tema usa View Transitions (desligada com `prefers-reduced-motion`). Nada fica escondido se o script falhar.
- **Repositórios privados sem link.** AugustusApp e o Conector WhatsApp aparecem sem link de código.

## Hospedagem

GitHub Pages, sem etapa de build.
