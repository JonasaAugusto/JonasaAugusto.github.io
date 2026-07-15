# Autonomous AI Lead Conversion Platform — Credit & Energy

[🇧🇷 Português](f5-platform-case-study.md) | 🇺🇸 English

**Technical Case Study | F5 Tecnologia | 2026**

> Project: Distributed platform that receives leads via WhatsApp, runs autonomous service with an AI agent,
> collects data, creates credit proposals (Crefaz), and routes leads to energy programs (Órigo/Evolua).
> Architecture: 2 distributed VPS with intelligent workload separation.
> Status: 24/7 production, serving real leads.

---

## 🏗️ Distributed Architecture

### Identified Problem

Initially, all logic ran on a single VPS:
- Inbound webhook (Meta WhatsApp)
- Orchestrator (state machine)
- AI agent (LLM)
- Browser automation (Playwright)

**Identified bottleneck:** Playwright (browser RPA for energy portals) consumed CPU/memory heavily,
affecting real-time service responsiveness (latency increased during portal submissions).

### Design Decision

Provision a dedicated VPS #2 with FastAPI isolating heavy RPA.

```
┌─────────────────────┐              ┌──────────────────────┐
│   VPS #1 (Light)    │              │   VPS #2 (Strong)    │
│                     │              │                      │
│ • WABA webhook      │── HTTP RPC ─>│ • Dedicated FastAPI  │
│ • AI agent          │              │ • Headless Playwright│
│ • 9-step flow       │<─────────────│ • Browser RPA        │
│ • Orchestration     │              │ • Result             │
│                     │              │                      │
└─────────────────────┘              └──────────────────────┘
```

**Benefit:** Isolation of responsibilities, no resource contention, more stable service.

---

## 🤖 Technical Components

### Generative AI Agent

- **Model:** OpenAI GPT (with fallback)
- **Prompt Engineering:** Structured per stage (greeting → coverage → data collection → bill → offer → complementary data → documents → confirmation → registration)
- **Context:** Isolated per lead (prevents leakage between conversations)
- **Guardrails:** Anti-hallucination (never confirms a result without a real API response)
- **Humanization:** Anti-repetition variation (protecting Meta's "repeated number" metric), confident progress language

### OCR & Computer Vision

Pipeline that reads customers' electricity bills:
- **Input:** Photo or PDF of the bill
- **Extraction:** Installation number, reading date, consumption in kWh
- **PDF handling:** Support for password-protected files
- **Error detection:** Identifies unreadable images, automatically requests resubmission
- **Output:** Structured, ready for routing decision

### API Integration

#### Crefaz (Credit)
1. **Pre-analysis:** CPF + basic data
2. **Simulation:** Available offers per agreement
3. **Selection:** User picks an offer
4. **Document Upload:** ID photo, selfie with document, bill photo
5. **Finalization:** Electronic signature (step3 → step7)
6. **Async Polling:** Checks status (situacaoId) until final outcome

#### Órigo & Evolua (Energy)
- **Goal:** Register customers in energy discount programs
- **Automation:** Full portal navigation (login → data → consumption → plan → contract)
- **Tech:** Headless Playwright on VPS #2
- **Result:** Signed contract, registered customer

### State Machine

9-step flow with per-lead isolated persistence:

```
1. Greeting (welcome)
   ↓
2. Coverage (checks whether the customer can access energy)
   ↓
3. Data Collection (name, CPF, phone, ZIP code)
   ↓
4. Bill (requests photo/PDF of the electricity bill)
   ↓
5. Credit Offer (simulation + selection + document submission)
   ↓
6. Complementary Data (completes credit information)
   ↓
7. Document Submission (upload of ID + selfie + bill)
   ↓
8. Confirmation (proposal summary, final confirmation)
   ↓
9. Energy Registration (routes to Órigo or Evolua by consumption/state)
```

Each step is saved to the database, allowing resumption if the conversation drops.

### Intelligent Energy Orchestration

**Decision:** Route each lead to the right partner based on:
- **kWh consumed:** Órigo for low consumption, Evolua for high
- **State coverage:** Some states only have one partner
- **State (UF) derivation:** If the state is missing from the input, it is computed from the ZIP code (by ranges, no external call)

Result: The customer reaches the right partner on the first attempt.

---

## 🔴 Challenges Solved

### 1. Dead Webhook — 43 Frozen Proposals

**Symptom:**
A partner's outcome webhook stopped being delivered (0 calls received for 4 days).
Result: 43 proposals stuck in "processing" status (lost sales).

**Tracing:**
- Cross-checked nginx logs (are requests arriving?)
- Database state (is proposta_id saved?)
- External API polling (did the status change?)
- Discovered: the endpoint was responding 200 OK, but webhook delivery had silently stopped on the partner's server

**Implemented Solution:**
systemd job (timer) doing active polling every 5 minutes:
```ini
[Unit]
Description=Outcome Recovery Poller
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

**Impact:**
- Recovered 43 APPROVED proposals that were frozen
- Resolved 140 DENIED proposals stuck in "processing"
- Reduced the stuck-lead backlog from 28 to 3

**Root cause:**
The proposal identifier was only stored in local memory and never reached the database. Fixed persistence in the ORM.

### 2. Race Condition in Human Takeover

**Symptom:**
When a human agent joined a conversation (via Chatwoot), the bot did NOT pause.
Result: Bot + agent replying simultaneously, confusing the customer.

**Diagnosis:**
- The pause check was performed only once, at the beginning
- If the agent joined during AI processing, the pause was not respected
- Classic race condition: state changes during processing

**Solution:**
Robust phone matching + a re-check guard immediately before sending:

```python
def should_reply(phone):
    # Normalize: remove 55, add 9th digit, etc
    normalized_phone = normalize_phone(phone)

    # Check pause in database
    conversation = db.get_conversation(normalized_phone)

    # RE-CHECK 100ms before sending
    time.sleep(0.1)
    conversation_refresh = db.get_conversation(normalized_phone)

    # Only reply if BOTH checks indicate not paused
    return not conversation.paused and not conversation_refresh.paused
```

**Impact:**
Human handoff is now safe. No simultaneous replies.

### 3. Latency Optimization in the OCR Pipeline

Not a critical case, but optimized:
- **Before:** OCR + routing decision + submission took 8s
- **After:** Smart cache with TTL, request batching (3.2s)
- **Tech:** Redis for ZIP → state cache, optimized Supabase query

---

## 💾 Persistence & Data

### PostgreSQL Modeling (Supabase)

```sql
-- Leads
CREATE TABLE leads (
    id UUID PRIMARY KEY,
    telefone VARCHAR(20),
    cpf VARCHAR(11),
    estado_atual INT, -- 1-9 (state machine)
    dados_coletados JSONB, -- name, email, ZIP, etc
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Credit Proposals
CREATE TABLE propostas (
    id UUID PRIMARY KEY,
    lead_id UUID REFERENCES leads(id),
    proposta_id_crefaz VARCHAR(50), -- ID at the partner bank
    situacao_id INT, -- Crefaz status
    valor DECIMAL,
    juros DECIMAL,
    aprovada BOOLEAN,
    sync_webhook BOOLEAN, -- Recovery flag
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Energy (Routing)
CREATE TABLE energia_rota (
    id UUID PRIMARY KEY,
    lead_id UUID REFERENCES leads(id),
    kwh_consumo DECIMAL,
    parceiro VARCHAR(20), -- 'origo' or 'evolua'
    uf VARCHAR(2),
    status VARCHAR(20), -- 'pendente', 'cadastrado', 'erro'
    created_at TIMESTAMP
);
```

### Versioned Migrations

All schema changes are versioned (`migrations/001_initial.sql`, `002_add_sync_webhook_flag.sql`, etc).

---

## 📊 Observability & Monitoring

### Flask Dashboard (Real Time)

```
┌─────────────────────────┬──────────────────────────────┐
│  CREDIT FUNNEL          │  ENERGY FUNNEL               │
│  Entered: 156           │  Órigo: 89                   │
│  Simulated: 142         │  Evolua: 54                  │
│  Offers: 128            │  None: 13                    │
│  Confirmed: 91          │                              │
│                         │  kWh distribution:           │
│  Conversion rate: 58%   │  < 100: 12 | 100-300: 89     │
│                         │  > 300: 55                   │
├─────────────────────────┼──────────────────────────────┤
│  WABA HEALTH            │  VPS METRICS                 │
│  Numbers: 3             │  VPS#1 CPU: 34% | RAM: 61%   │
│  Messages today: 487    │  VPS#2 CPU: 72% | RAM: 45%   │
│  Blocks: 0              │  Uptime: 99.97%              │
└─────────────────────────┴──────────────────────────────┘
```

### Structured Logging

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

### Automatic Alerts

- VPS #1 CPU > 80% for 2min → Slack alert
- VPS #2 RAM > 85% → Slack alert
- Dead webhook (0 calls in 30min) → Slack + Email alert
- Poller job failed → Automatic restart via systemd

---

## 🔒 Security & Compliance

### Sensitive Data Handling (LGPD)

- **CPF, ID, Selfie:** Encrypted at rest (Supabase)
- **Transmission:** HTTPS (TLS 1.3), JWT authentication
- **Retention:** Delete policy after 90 days (LGPD)
- **Access:** Logs of who accessed which data, and when

### Anti-Fraud Mitigation

Energy partners have rate limits and suspicious behavior detection.
Strategy: **Throttling** (space out submissions, never burst):

```python
async def submit_energy_form(lead_id, data):
    await asyncio.sleep(0.5)  # Space out requests
    response = await client.post(url, json=data)

    if response.status_code == 429:  # Rate limit
        logger.warning("Energy rate limit, exponential backoff")
        await asyncio.sleep(5)  # Wait before retry
        return await submit_energy_form(lead_id, data)

    return response
```

Result: Never burns an IP in production.

### Customer Privacy

- Never leaks technical content (HTTP 4xx/5xx filtered before reaching the customer)
- Webhook authentication (WABA signature)
- Token management with automatic renewal (auto-refresh 15min before expiry)
- LLM context isolation (no lead A info leaks to lead B)

---

## ⚡ Infrastructure & DevOps

### systemd Services on VPS #1

```
webhook_listener.service          → Listens to WABA webhook
app_orquestrador.service          → State machine + LLM
rpa_client.service                → HTTP client for VPS #2
poller_desfecho.timer / .service  → Recovery job (5min)
watchdog_sync.timer / .service    → State synchronization (10min)
token_refresh.timer / .service    → Token renewal (60min)
```

Each with:
- Auto-restart on failure
- Health endpoint (`/health`)
- Structured logging
- OOM priority

### systemd Services on VPS #2

```
fastapi_rpa.service               → Dedicated Playwright API
```

### Public Endpoint (nginx + Certbot)

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

**Benefit:** Permanent, stable URL (replaced ephemeral cloudflared).

### Residential Proxy

Some partners block datacenter IPs.
Solution: Residential proxy layer routing energy traffic through real residential IPs.

```
Request → VPS #2 → Residential Proxy → Partner (trusts residential IP)
```

---

## 🧠 Diagnostic Methodology

Three principles guiding every problem:

1. **From Symptom to Root Cause:** Never assume a cause, always trace with data
2. **Systemic Normalization:** When a problem appeared (phone format), it was fixed so it never comes back
3. **Evidence Before Conclusion:** Logs, database state, or a controlled test

Example: "The bot says 'processing' too often" → Logs show a dead webhook → Recovery via poller.

---

## 📈 Metrics & Impact

| Metric | Value |
|--------|-------|
| **Leads served (24h)** | ~200 |
| **Conversion rate (collection → offer)** | 82% |
| **Approval rate (credit)** | 58% |
| **Average latency (question → answer)** | 1.2s |
| **Availability (uptime)** | 99.97% |
| **Recovered proposals (dead webhook)** | 43 |
| **Stuck backlog (before)** | 28 leads |
| **Stuck backlog (after)** | 3 leads |
| **Race conditions solved** | 1 (human takeover) |

---

## 🛠️ Technology Stack

**Backend & Orchestration:**
- Python 3.11
- FastAPI (framework)
- Flask (dashboard)

**AI & LLM:**
- OpenAI API (GPT-4)
- LangChain (agent orchestration)
- Structured Prompt Engineering

**Automation & RPA:**
- Playwright (headless browser)
- Python asyncio (concurrency)

**Database:**
- PostgreSQL (Supabase)
- Redis (cache)

**Integration:**
- Meta WhatsApp Business API (WABA)
- Chatwoot (service CRM)
- Crefaz API (credit)
- Órigo & Evolua portals (scraping)

**Infrastructure:**
- 2 Linux VPS (Ubuntu 22.04)
- systemd (service orchestration)
- nginx (reverse proxy)
- Certbot (automatic HTTPS)
- Git (versioning)

**Monitoring:**
- Structured logging (JSON)
- Flask dashboard (real time)
- Slack/Email alerts

---

## 🏁 Conclusion

A production platform balancing:
- **Technical complexity** (AI + RPA + multi-API integration)
- **Reliability** (retry, fallback, polling, watchdogs)
- **Scalability** (2 isolated VPS, smart caching)
- **Observability** (logs, dashboard, alerts)

Every decision was driven by a real problem identified in production.

---

*Technical document updated in May 2026. Platform operating 24/7.*
