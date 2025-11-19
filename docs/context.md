# CONTEXTO.MD – Polymarket AI Hedge Agent 

## Objetivo del MVP
Construir un agente **AI-driven** (autónomo con lógica smart + optional LLM) que tradea en Polymarket:
- **Ejemplo**: Apuesta inicial $1000 en "Yes" (80% prob) para "Will Bitcoin go below 90k?"
- **Lógica core**: Monitorea prob → si ≥85%: book profit (sell YES) + rebalance (buy NO para hedge) → lockea ganancia.
- **Si ≤78%**: Cut loss (sell all) y exit.
- **AI twist**: Usa RAG/LLM para ajustar thresholds basados en news/sentiment (e.g., "BTC news bajista? Baja stop-loss a 75%").

## Stack Obligatorio (Basado en Resources)
- **Framework base**: Fork de [Polymarket/agents](https://github.com/Polymarket/agents) – Usa `Gamma.py` para data, `Polymarket.py` para trades, `trade.py` para ejecución.
- **Python 3.9+**, `requirements.txt` de agents + extras (web3, openai).
- **API**: Gamma para mercados/precios, CLOB para orders (via agents).
- **Wallet**: PRIVATE_KEY en .env → Polygon Amoy testnet (CHAIN_ID=80002).
- **Real-time**: Polling 15s o WebSocket via agents CLI.
- **Persistencia**: position.json (extiende Objects.py de agents).
- **AI**: Prompts en `cli.py` para decisions (e.g., "Evalúa si hedgear basado en prob 0.85 + news").

## Mercado de Ejemplo (Hardcode)
- Slug: "will-bitcoin-go-below-90k-before-dec-31-2025" (verifica via `cli.py get-all-markets --slug bitcoin`).
- Condition ID: Fetch via Gamma API (e.g., 0x9c8f...).
- Tokens: YES (outcome=0), NO (outcome=1).

## Funciones Mínimas (Extiende agents)
1. `get_current_prob(market_slug)` → float (YES price de Gamma.py).
2. `get_position(address, condition_id)` → {yes_shares, no_shares, pnl} (de Objects.py).
3. `place_order(condition_id, outcome_index:0/1, shares, price=None)` → Via Polymarket.py.
4. `book_profit_and_hedge(prob, position)` → Sell % YES → Buy NO con proceeds.
5. `cut_loss_and_exit(position)` → Sell all.
6. `ai_adjust_thresholds(prob, news_context)` → LLM prompt: "Ajusta take-profit basado en esto?" (opcional).
7. Main loop: While True → fetch → decide (rules + AI) → trade → save state.

## Test Scenarios (3 Mínimos, con Tablas)
1. **Profit + Hedge**: 80% → 86% → Sell 100% YES ($1062 cash) → Buy NO → Locked +$62.
2. **Loss Cut**: 80% → 76% → Sell all → Exit con -$40.
3. **AI Scenario**: 80% → 85% + news bajista → LLM ajusta a 82% → No hedgea aún.

## Entregables
- Repo: Fork de agents + tus cambios.
- README.md: Setup (incluye fundear testnet USDC).
- ARCHITECTURE.md: Diagrama + flows.
- tests/report.md: Tablas Markdown + PnL calcs.
- Optional: Discussion.md (riesgos: slippage, LLM hallucinations; improvements: Multi-mercado con Grok API).

## Notas
- **Seguridad**: Nunca commit .env; usa testnet.
- **Escalabilidad**: Agents soporta Docker para prod.
- Deadline: 21 nov → Prioriza rules > AI full.