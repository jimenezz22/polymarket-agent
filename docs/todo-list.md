# To-Do List por Fases – Polymarket AI Hedge Agent
## Deadline: 21 nov 2025 23:59 | Hoy: 19 nov 2025

### FASE 0 – Setup Inicial (30-60 min, HOY)
- [ ] Fork/clone Polymarket/agents: `git clone https://github.com/Polymarket/agents.git polymarket-hedge-agent`
- [ ] Push a tu GitHub repo (público para submit).
- [ ] Estructura: Agrega carpetas `/my_agent` (strategy), `/tests`, `/docs` (usa base de agents).
- [ ] `.env`: Copia `.env.example`, agrega PRIVATE_KEY (testnet), OPENAI_API_KEY (opcional).
- [ ] `pip install -r requirements.txt` + `web3 openai` (extras).
- [ ] Test CLI: `python scripts/python/cli.py get-all-markets --slug bitcoin` → Ver probs reales.
- [ ] Commit: "feat: fork agents + env setup"

### FASE 1 – Integración Base + Data/Wallet (1-2 horas, HOY/MAÑANA)
- [ ] Wrapper en `my_agent/api_wrapper.py`: Extiende Gamma.py para `get_current_prob(slug)`.
- [ ] Wallet test: Usa Polymarket.py → `client = Polymarket(private_key=...)` → get_balance USDC.
- [ ] Fetch posición inicial: Compra $1000 YES via CLI o script (testnet).
- [ ] Persistencia: Extiende Objects.py → Position model con yes_shares, pnl.
- [ ] Test: Log prob cada 10s → "Current YES prob: 0.82".
- [ ] Commit: "feat: api + wallet integration"

### FASE 2 – Position Manager + Estado (1 hora, MAÑANA)
- [ ] Clase `HedgePosition` (Pydantic): Track shares, avg_cost, calculate_pnl(yes_price, no_price).
- [ ] `position.json`: Save/load post-trade (integra a trade.py).
- [ ] `is_hedged()`: True si both sides >0 y pnl_locked >0.
- [ ] Test: Simula buy inicial → save state.
- [ ] Commit: "feat: position tracking"

### FASE 3 – Core Strategy (Rule-Based, 2-3 horas, 20 nov)
- [ ] En `my_agent/strategy.py`: `should_take_profit(prob)` (≥0.85), `should_cut_loss(prob)` (≤0.78).
- [ ] `book_profit_and_hedge(position)`: Sell 100% YES → calc proceeds → buy max NO → update state.
- [ ] `cut_loss_and_exit()`: Sell all → reset position.
- [ ] Math hedging: `no_shares = proceeds / (1 - yes_prob)` → Log "Locked profit: $62".
- [ ] Integra a `agents/application/trade.py`: Llama strategy en loop.
- [ ] Commit: "feat: trading logic + hedging"

### FASE 4 – Main Loop + AI Layer (1-2 horas, 20 nov)
- [ ] `main.py`: While loop → fetch prob → eval strategy → execute via Polymarket.py → sleep 15s.
- [ ] Logging: Rich console (de agents) + "AI Check: Prompting LLM...".
- [ ] AI optional: `ai_decide( prob, news )` → Prompt: "Ajusta threshold? Respuesta: JSON {new_threshold: 0.83}".
- [ ] Error handling: Retry API, slippage check.
- [ ] Commit: "feat: main loop + basic AI"

### FASE 5 – Tests & Report (2 horas, 20 nov)
- [ ] `tests/backtest.py`: Simula 3 escenarios con historical (de FinFeed o mock).
- [ ] `tests/report.md`: Tablas | Tiempo | Prob | Acción | Shares | PnL | (e.g., +15% locked).
- [ ] Run: `pytest` + CLI tests.
- [ ] Commit: "test: full scenarios + report"

### FASE 6 – Docs & Polish (1-2 horas, 21 nov)
- [ ] README.md: Setup (incluye agents fork), run `python main.py`, ejemplo log.
- [ ] ARCHITECTURE.md: Diagrama Mermaid + flows (usa tu versión anterior).
- [ ] docs/DISCUSSION.md: Riesgos (gas, LLM bias), improvements (Grok integration).
- [ ] Opcional: Streamlit app para demo (live prob + PnL).
- [ ] Tag: `v1.0-ai-hedge-mvp`.
- [ ] Commit: "docs: full documentation"

### FASE 7 – Submit (21 nov <23:59)
- [ ] Repo público + README con "Built on Polymarket/agents + custom AI hedging".
- [ ] Email: Subject exacto, body: "Link repo + test report highlights + ofrezco demo".
- [ ] Backup: Zip si Git falla.