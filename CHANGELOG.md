# Changelog

## [Não publicado] - 1.1.0

### Auditoria de portfólio (posicionamento, credibilidade, performance)
- Cargo "CEO" virou "Fundador e Engenheiro de Software" no site e nos CVs; posicionamento "Engenheiro de Software, backend em Python e C#" (título, metatags, JSON-LD, og-image).
- Topo com a prova na primeira tela: 73,7 s para 0,08 s, 43% para ~89% e 595 testes do Orchestrator, cada um com link para a fonte.
- Removidas frases defensivas ("Não é vibe coding", "Não há métrica de antes e depois").
- Corrigido contra repositórios, PyPI e CI: Orchestrator está no PyPI (v1.5.1), suíte completa roda também no Windows, contagem de 595 testes, versão 1.4.0 vs 1.5.1.
- Estudos de caso saem dos modais para páginas próprias (`/casos/<caso>/`, `/en/cases/<caso>/`); HTML principal menor.
- Nova pipeline `src/` + `scripts/build.py` (substitui `scripts/gerar-en.py`): CSS inline, caminhos por profundidade, `sitemap.xml` com hreflang, JSON-LD, `robots.txt`, `404.html`.
- Contato refeito (links grandes, currículo em PDF logo abaixo do e-mail); CV com IAprovale e Orchestrator, ainda em 1 página.
- Acessibilidade: axe (WCAG 2.2 AA) sem violações em 9 páginas, 2 temas, 390 e 1440 px; região rolável da tabela da F5 focável; botões do topo em grade 2x2 no celular.

### Reformulação para leitura rápida (recrutador)
- Topo sem rolar: frase de apresentação, botões (e-mail, GitHub, LinkedIn, currículo), 3 números com antes e depois e 3 projetos em destaque (IAprovale, AI Agents Orchestrator, F5 Tecnologia).
- Projetos em destaque no formato problema, o que fiz, o que quebrou, o que faria diferente, resultado e limitação. AugustusApp, NotaME, Conector WhatsApp e Fabula Coop passam para "Outros projetos" (`<details>` fechado).
- Stack: principais (Python, FastAPI, PostgreSQL, Docker, Linux), secundárias em uma linha e grupo de IA com o projeto de cada ferramenta; lista completa recolhida.
- Novas seções "Como eu uso IA no meu trabalho" e "Como o DeepSeek é usado no IAprovale" (a partir do código do backend, com o que ainda não está pronto).
- Inglês estático em `/en/`, gerado por `scripts/gerar-en.py`; alternador de idioma vira link; `hreflang`, `canonical` e metatags por idioma. Testes em `scripts/testar-site.py`.
- Certificações AWS e Azure como "Planejado · início em fev/2027" (site e currículos); Claude e Codex só no projeto Orchestrator; PDFs do currículo regenerados.
- Leitura em camadas: resultados em produção e experiência primeiro (F5 em destaque), projetos com problema e resultado à vista e o restante em "Ver detalhes" (abre no próprio lugar); stack com a IA recolhida; IA no trabalho, DeepSeek, desafios e formação viram extras fechados por padrão. Links para dentro de blocos fechados abrem o bloco.
- Header sem fundo translúcido e que só esconde depois de uma rolagem contínua (sem piscar ao rolar ou abrir blocos); separação maior e título "Os projetos por trás desses números" antes da lista de projetos.
- Removido o formulário de contato (redundante com e-mail e links); o contato fica por e-mail, LinkedIn, Instagram e GitHub, sem serviço de terceiro.
- Voltam as animações e os hovers do site anterior: nome que sobe ao carregar, entradas ao rolar, números que contam, prévia que segue o cursor nos outros projetos, botões magnéticos, hora local, barra de progresso e palavra do rodapé. O topo ocupa a tela inteira e as métricas aparecem ao rolar. Movimento reduzido só faz fade curto.
- Removidos: quadros decorativos soltos e o formulário.

### Adicionado
- Estudo de caso do AI Agents Orchestrator (v1.4.0) em "Mais projetos": problema, solução, decisões, resultados verificáveis e o que ainda não está pronto (PT/EN), em um novo diálogo.
- Estudo de caso "Venda automatizada no WhatsApp: de 43% para ~89% de cadastros concluídos" no painel da F5, com contexto, diagnóstico, correções, tabela de resultados e forma de trabalho (PT/EN); substitui a versão anterior do mesmo caso ("Cadastro automático ~20% mais rápido"). O painel tem navegação entre os dois casos.
- Instagram pessoal (jonasaaugusto) e da Augustus AI (augustusaisolutions) na seção de contato e no rodapé.

### Alterado
- Blocos de métricas em número ímpar ocupam a largura toda na última célula no celular, sem célula vazia.
- E-mail de contato agora é jonasaugustosantosoliveira@gmail.com (página inicial e currículos PT/EN).
