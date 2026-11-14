# Changelog

## [Não publicado] - 1.1.0

### Reformulação para leitura rápida (recrutador)
- Topo sem rolar: frase de apresentação, botões (e-mail, GitHub, LinkedIn, currículo), 3 números com antes e depois e 3 projetos em destaque (IAprovale, AI Agents Orchestrator, F5 Tecnologia).
- Projetos em destaque no formato problema, o que fiz, o que quebrou, o que faria diferente, resultado e limitação. AugustusApp, NotaME, Conector WhatsApp e Fabula Coop passam para "Outros projetos" (`<details>` fechado).
- Stack: principais (Python, FastAPI, PostgreSQL, Docker, Linux), secundárias em uma linha e grupo de IA com o projeto de cada ferramenta; lista completa recolhida.
- Novas seções "Como eu uso IA no meu trabalho" e "Como o DeepSeek é usado no IAprovale" (a partir do código do backend, com o que ainda não está pronto).
- Inglês estático em `/en/`, gerado por `scripts/gerar-en.py`; alternador de idioma vira link; `hreflang`, `canonical` e metatags por idioma. Testes em `scripts/testar-site.py`.
- Certificações AWS e Azure como "Planejado · início em fev/2027" (site e currículos); Claude e Codex só no projeto Orchestrator; PDFs do currículo regenerados.
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
