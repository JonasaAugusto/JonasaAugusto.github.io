# Plataforma Autônoma de Conversão de Leads com IA — Crédito & Energia

🇧🇷 Português | [🇺🇸 English](f5-platform-case-study.en.md)

**Caso de Estudo Técnico | F5 Tecnologia | 2026**

> Projeto: Plataforma distribuída que recebe leads via WhatsApp, conduz atendimento autônomo com agente de IA,
> coleta dados, gera propostas de crédito junto a um parceiro financeiro e roteia leads para programas de energia.
> Arquitetura: 2 VPS distribuídas com separação inteligente de workload.
> Status: Produção 24/7, atendendo leads reais.
>
> *Observação: nomes de parceiros comerciais e detalhes proprietários foram omitidos por confidencialidade. Este documento descreve arquitetura, decisões técnicas e resultados.*

---

## 🏗️ Arquitetura Distribuída

### Problema Identificado

Inicialmente, toda a lógica rodava em uma única VPS:
- Webhook de entrada (Meta WhatsApp)
- Orquestrador (máquina de estados)
- Agente de IA (LLM)
- Automação de navegador (Playwright)

**Gargalo identificado:** Playwright (RPA de navegador para portais de energia) consumia CPU/memória pesadamente,
afetando a responsividade do atendimento em tempo real (latência aumentava durante submissões em portais).

### Decisão de Design

Provisionar VPS #2 dedicada com FastAPI isolando RPA pesado.

```
┌─────────────────────┐              ┌──────────────────────┐
│   VPS #1 (Fraca)    │              │   VPS #2 (Forte)     │
│                     │              │                      │
│ • Webhook WABA      │── HTTP RPC ─>│ • FastAPI dedicada   │
│ • Agente IA         │              │ • Playwright headless│
│ • Fluxo 9 etapas    │<─────────────│ • RPA de navegador   │
│ • Orquestração      │              │ • Resultado          │
│                     │              │                      │
└─────────────────────┘              └──────────────────────┘
```

**Benefício:** Isolamento de responsabilidades, sem contenção de recursos, atendimento mais estável.

---

## 🤖 Componentes Técnicos

### Agente de IA Generativa

- **Modelo:** OpenAI GPT (com fallback)
- **Engenharia de Prompt:** Estruturada por etapa (saudação → cobertura → coleta → fatura → oferta → dados complementares → documentos → confirmação → registro)
- **Contexto:** Isolado por lead (evita vazamento entre conversas)
- **Guardrails:** Anti-alucinação (nunca confirma resultado sem retorno real da API)
- **Humanização:** Variação anti-repetição (proteção da métrica Meta de "número repetido"), linguagem de progresso confiante

### OCR & Visão Computacional

Pipeline que lê contas de luz do cliente:
- **Input:** Foto ou PDF da conta
- **Extração:** Número de instalação, data de leitura, consumo em kWh
- **Tratamento de PDF:** Suporte a arquivos protegidos por senha
- **Detecção de erro:** Identifica imagens ilegíveis, solicita reenvio automaticamente
- **Saída:** Estruturada, pronta para decisão de rota

### Integração de APIs

#### Parceiro de Crédito (API)
1. **Pré-análise:** CPF + dados básicos
2. **Simulação:** Ofertas disponíveis por convênio
3. **Seleção:** Usuário escolhe oferta
4. **Upload de Documentos:** Foto de RG, selfie com documento, foto de fatura
5. **Finalização:** Assinatura eletrônica (fluxo multi-etapa)
6. **Polling Assíncrono:** Verifica status até desfecho final

#### Parceiros de Energia (Portais Web)
- **Objetivo:** Cadastro de cliente em programas de desconto de energia
- **Automação:** Navegação completa do portal (login → dados → consumo → plano → contrato)
- **Tech:** Playwright headless em VPS #2
- **Resultado:** Contrato assinado, cliente cadastrado

### Máquina de Estados

Fluxo de 9 etapas com persistência isolada por lead:

```
1. Saudação (boas-vindas)
   ↓
2. Cobertura (verifica se cliente pode acessar energia)
   ↓
3. Coleta de Dados (nome, CPF, telefone, CEP)
   ↓
4. Fatura (solicita foto/PDF da conta de luz)
   ↓
5. Oferta de Crédito (simulação + seleção + envio de docs)
   ↓
6. Dados Complementares (complementa info para crédito)
   ↓
7. Envio de Documentos (upload de RG + selfie + fatura)
   ↓
8. Confirmação (resumo da proposta, confirmação final)
   ↓
9. Registro em Energia (roteia para o parceiro adequado conforme consumo/estado)
```

Cada etapa é salva no banco, permitindo retomada se conversa cair.

### Orquestração Inteligente de Energia

**Decisão:** Rotear cada lead para o parceiro correto baseado em:
- **kWh consumido:** parceiro A para baixo consumo, parceiro B para alto
- **Cobertura estatal:** Alguns estados só têm um parceiro
- **Derivação de UF:** Se UF não está na entrada, calcula a partir do CEP (por faixas, sem chamada externa)

Resultado: Cliente vai para o parceiro certo na primeira tentativa.

---

## 🔴 Desafios Resolvidos

### 1. Webhook Morto — 43 Propostas Congeladas

**Sintoma:**
Webhook de desfecho de um parceiro parou de ser entregue (0 chamadas recebidas por 4 dias).
Resultado: 43 propostas em status "processando" (venda perdida).

**Rastreamento:**
- Cruzei logs de nginx (requisições chegam?)
- Estado no banco (proposta_id está salvo?)
- Polling da API externa (status mudou?)
- Descobri: endpoint estava respondendo 200 OK, mas a entrega de webhook tinha parado silenciosamente no servidor parceiro

**Solução Implementada:**
Job systemd (timer) que faz polling ativo a cada 5 minutos:
```ini
[Unit]
Description=Poller de Recuperação de Desfecho
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /app/jobs/poller_desfecho.py
User=app

[Install]
WantedBy=timers.target

[Timer]
OnBootSec=2min
OnUnitActiveSec=5min
```

**Impacto:**
- Recuperei 43 propostas APROVADAS que estavam congeladas
- Resolvi 140 propostas NEGADAS presas em "processando"
- Reduzi backlog de leads travados de 28 para 3

**Raiz:**
Identificador da proposta era salvo só em memória local e nunca chegava ao banco. Corrigi persistência no ORM.

### 2. Race Condition em Takeover Humano

**Sintoma:**
Quando um atendente humano entrava em uma conversa (via Chatwoot), o bot NÃO pausava.
Resultado: Bot + atendente respondendo simultaneamente, confundindo o cliente.

**Diagnóstico:**
- Verificação de pausa era feita uma única vez no início
- Se atendente entrasse durante o processamento da IA, a pausa não era respeitada
- Race condition clássica: estado muda durante o processamento

**Solução:**
Casamento robusto de telefone + guarda de re-check imediatamente antes de enviar:

```python
def deve_responder(telefone):
    # Normalizar: remover 55, adicionar 9º dígito, etc
    telefone_normalizado = normalizar_telefone(telefone)

    # Verificar pausa em banco
    conversa = db.get_conversa(telefone_normalizado)

    # RE-VERIFICAR 100ms antes de enviar
    time.sleep(0.1)
    conversa_refresh = db.get_conversa(telefone_normalizado)

    # Só responde se AMBAS verificações indicam não pausado
    return not conversa.pausado and not conversa_refresh.pausado
```

**Impacto:**
Handoff humano agora é seguro. Nenhuma resposta simultânea.

### 3. Otimização de Latência no Pipeline OCR

Não foi caso crítico, mas otimizei:
- **Antes:** OCR + decisão de rota + envio levava 8s
- **Depois:** Cache inteligente com TTL, batching de requisições (3.2s)
- **Tech:** Redis para cache de CEP → UF, Supabase query otimizada

---

## 💾 Persistência & Dados

### Modelagem PostgreSQL (Supabase)

```sql
-- Leads
CREATE TABLE leads (
    id UUID PRIMARY KEY,
    telefone VARCHAR(20),
    cpf VARCHAR(11),
    estado_atual INT, -- 1-9 (máquina de estados)
    dados_coletados JSONB, -- nome, email, CEP, etc
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Propostas de Crédito
CREATE TABLE propostas (
    id UUID PRIMARY KEY,
    lead_id UUID REFERENCES leads(id),
    proposta_id_parceiro VARCHAR(50), -- ID no parceiro de crédito
    situacao_id INT, -- Status no parceiro
    valor DECIMAL,
    juros DECIMAL,
    aprovada BOOLEAN,
    sync_webhook BOOLEAN, -- Flag de recuperação
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Energia (Rota)
CREATE TABLE energia_rota (
    id UUID PRIMARY KEY,
    lead_id UUID REFERENCES leads(id),
    kwh_consumo DECIMAL,
    parceiro VARCHAR(20), -- identificador do parceiro de energia
    uf VARCHAR(2),
    status VARCHAR(20), -- 'pendente', 'cadastrado', 'erro'
    created_at TIMESTAMP
);
```

### Migrações Versionadas

Todas as mudanças em schema são versionadas (`migrations/001_initial.sql`, `002_add_sync_webhook_flag.sql`, etc).

---

## 📊 Observabilidade & Monitoramento

### Dashboard Flask (Tempo Real)

```
┌─────────────────────────┬──────────────────────────────┐
│  FUNIL DE CRÉDITO       │  FUNIL DE ENERGIA            │
│  Entrados: 156          │  Parceiro A: 89              │
│  Simulados: 142         │  Parceiro B: 54              │
│  Ofertas: 128           │  Nenhum: 13                  │
│  Confirmados: 91        │                              │
│                         │  Distribuição kWh:           │
│  Taxa conversão: 58%    │  < 100: 12 | 100-300: 89     │
│                         │  > 300: 55                   │
├─────────────────────────┼──────────────────────────────┤
│  SAÚDE WABA             │  MÉTRICAS VPS                │
│  Números: 3             │  VPS#1 CPU: 34% | RAM: 61%   │
│  Mensagens hoje: 487    │  VPS#2 CPU: 72% | RAM: 45%   │
│  Bloqueios: 0           │  Uptime: 99.97%              │
└─────────────────────────┴──────────────────────────────┘
```

### Logging Estruturado

```python
import logging
import json

logger = logging.getLogger(__name__)

logger.info(json.dumps({
    "timestamp": "2026-05-15T14:23:45Z",
    "event": "webhook_received",
    "lead_id": "abc123",
    "phone": "+55XX9XXXXXXXX",
    "stage": 5,
    "duration_ms": 234
}))
```

### Alertas Automáticos

- VPS #1 CPU > 80% por 2min → Alerta Slack
- VPS #2 RAM > 85% → Alerta Slack
- Webhook morto (0 chamadas em 30min) → Alerta Slack + Email
- Job de poller falhou → Restart automático via systemd

---

## 🔒 Segurança & Conformidade

### Tratamento de Dados Sensíveis (LGPD)

- **CPF, RG, Selfie:** Criptografados em repouso (Supabase)
- **Transmissão:** HTTPS (TLS 1.3), autenticação via JWT
- **Retenção:** Política de delete após 90 dias (LGPD)
- **Acesso:** Logs de quem acessou qual dado, quando

### Respeito a Limites de Taxa (Rate Limiting)

Os serviços externos aplicam limites de requisições por origem. Para operar como um cliente
bem-comportado e não degradar a experiência, implementei **throttling** com backoff exponencial,
espaçando submissões e reagindo corretamente a respostas `429 Too Many Requests`:

```python
async def submeter_formulario_energia(lead_id, dados):
    await asyncio.sleep(0.5)  # Espaçar requisições (cliente educado)
    response = await client.post(url, json=dados)

    if response.status_code == 429:  # Rate limit
        logger.warning("Limite de taxa atingido, aplicando backoff exponencial")
        await asyncio.sleep(5)  # Aguarda antes de nova tentativa
        return await submeter_formulario_energia(lead_id, dados)

    return response
```

Resultado: integração estável e sustentável, sem sobrecarregar os serviços parceiros.

### Privacidade do Cliente

- Nunca vaza conteúdo técnico (HTTP 4xx/5xx filtrados no retorno ao cliente)
- Autenticação em webhooks (assinatura WABA)
- Gestão de tokens com renovação automática (auto-refresh 15min antes de expirar)
- Isolamento de contexto LLM (nenhuma info de lead A vaza para lead B)

---

## ⚡ Infraestrutura & DevOps

### Serviços systemd em VPS #1

```
webhook_listener.service          → Escuta webhook WABA
app_orquestrador.service          → Máquina de estados + LLM
rpa_client.service                → Cliente HTTP para VPS #2
poller_desfecho.timer / .service  → Job de recuperação (5min)
watchdog_sync.timer / .service    → Sincronização de estado (10min)
token_refresh.timer / .service    → Renovação de token (60min)
```

Cada um com:
- Auto-restart em falha
- Endpoint de saúde (`/health`)
- Logging estruturado
- Prioridade OOM

### Serviços systemd em VPS #2

```
fastapi_rpa.service               → API dedicada de Playwright
```

### Endpoint Público (nginx + Certbot)

```nginx
server {
    listen 443 ssl http2;
    server_name api.f5leads.dev;

    ssl_certificate /etc/letsencrypt/live/api.f5leads.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.f5leads.dev/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header X-Forwarded-For $remote_addr;
    }
}
```

**Benefício:** URL permanente e estável (substituiu cloudflared efêmero).

### Camada de Rede Resiliente

Alguns serviços externos apresentavam conectividade instável a partir de faixas de IP de datacenter
(timeouts intermitentes e bloqueios por reputação de origem). Para garantir entrega confiável das
requisições em produção, adicionei uma camada de saída de rede configurável, isolando a política de
roteamento de saída da lógica de aplicação.

```
Requisição → VPS #2 → Camada de saída de rede → Serviço externo
```

**Benefício:** conectividade estável e previsível com serviços de terceiros, sem acoplar a lógica de
negócio a detalhes de infraestrutura de rede.

---

## 🧠 Metodologia de Diagnóstico

Três princípios que guiaram cada problema:

1. **Do Sintoma à Raiz:** Nunca assumo causa, sempre rastreio com dados
2. **Normalização Sistêmica:** Se vi um problema (formato de telefone), corrigi de forma que nunca volte
3. **Evidência Antes de Conclusão:** Log, estado no banco, ou teste controlado

Exemplo: "O robô fala muito 'estou processando'" → Log mostra webhook parado → Recuperação via poller.

---

## 📈 Métricas & Impacto

| Métrica | Valor |
|---------|-------|
| **Leads atendidos (24h)** | ~200 |
| **Taxa de conversão (coleta → oferta)** | 82% |
| **Taxa de aprovação (crédito)** | 58% |
| **Latência média (pergunta → resposta)** | 1.2s |
| **Disponibilidade (uptime)** | 99.97% |
| **Propostas recuperadas (webhook morto)** | 43 |
| **Backlog travado (antes)** | 28 leads |
| **Backlog travado (depois)** | 3 leads |
| **Race conditions resolvidas** | 1 (takeover humano) |

---

## 🛠️ Stack Tecnológico

**Backend & Orquestração:**
- Python 3.11
- FastAPI (framework)
- Flask (dashboard)

**IA & LLM:**
- OpenAI API (GPT-4)
- LangChain (orquestração de agente)
- Prompt Engineering estruturado

**Automação & RPA:**
- Playwright (navegador headless)
- Python asyncio (concorrência)

**Banco de Dados:**
- PostgreSQL (Supabase)
- Redis (cache)

**Integração:**
- Meta WhatsApp Business API (WABA)
- Chatwoot (CRM de atendimento)
- API de parceiro de crédito
- Portais de parceiros de energia (automação web)

**Infraestrutura:**
- 2 VPS Linux (Ubuntu 22.04)
- systemd (orquestração de serviços)
- nginx (proxy reverso)
- Certbot (HTTPS automático)
- Git (versionamento)

**Monitoramento:**
- Logging estruturado (JSON)
- Dashboard Flask (tempo real)
- Alertas Slack/Email

---

## 🏁 Conclusão

Plataforma em produção que equilibra:
- **Complexidade técnica** (IA + RPA + integração de múltiplas APIs)
- **Confiabilidade** (retry, fallback, polling, watchdogs)
- **Escalabilidade** (2 VPS isoladas, cache inteligente)
- **Observabilidade** (logs, dashboard, alertas)

Cada decisão foi motivada por um problema real identificado em produção.

---

*Documento técnico atualizado em Maio 2026. Plataforma em operação 24/7.*
