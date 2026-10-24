# Portfólio Jonas Augusto

Portfólio pessoal publicado em [jonasaaugusto.github.io](https://jonasaaugusto.github.io), em português e inglês.

## Stack

- **HTML, CSS e JavaScript puros**, sem framework, sem build e sem scripts de terceiros
- **Geist e Geist Mono** (variáveis, self-hosted em `assets/fonts/`); a mono aparece só em medidas, datas e stack
- **Formspark** recebe o formulário de contato (só o `action` do formulário, nenhum script externo)

## Estrutura

- `index.html`: página única, com o texto em PT no HTML e a tradução EN em atributos `data-en`
- `css/site.css`: tokens (cores dos temas claro e escuro, escala de tipo, espaçamento) e todos os estilos
- `js/site.js`: idioma, tema, menu, entradas das seções, números que contam, prévia que segue o cursor, diálogos do CV e do estudo de caso
- `cv.html` e `cv.en.html`: fonte do currículo (imprimir em PDF para atualizar); `JonasAugusto_cv_m.pdf` e `JonasAugusto_cv_en.pdf` são os PDFs de 1 página
- `docs/`: estudo de caso da F5 em Markdown (PT e EN)

## Decisões

- **Monocromático editorial.** Preto, branco e cinzas, com o amarelo do banner só no ponto de status e na seleção de texto. A tipografia faz o trabalho.
- **Tema claro e escuro.** Segue o sistema na primeira visita e guarda a escolha em `localStorage`; o script de tema roda no `<head>` para não piscar.
- **Movimento só com `transform` e `opacity`.** Entradas por IntersectionObserver, barra de leitura e progresso dos desafios com CSS scroll-driven (quando o navegador suporta), troca de tema e de idioma com View Transitions. Tudo desliga com `prefers-reduced-motion`, e nada fica escondido se o script falhar.
- **Interfaces desenhadas em HTML.** Os quadros dos projetos são fragmentos de interface feitos em HTML/CSS (não são screenshots), leves e nítidos em qualquer tela.
- **Repositórios privados sem link.** AugustusApp e o Conector WhatsApp aparecem sem link de código.

## Hospedagem

GitHub Pages, sem etapa de build.
