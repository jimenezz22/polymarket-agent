# Producto – Polymarket AI Hedge Agent MVP

## Descripción General
Un agente autónomo que gestiona apuestas en Polymarket con inteligencia híbrida: **reglas determinísticas** para trading seguro + **LLM opcional** para decisions contextuales (news/sentiment). Basado en Polymarket/agents, extiende trade.py para hedging automático. Corre en loop 24/7, protegiendo profits via rebalance.

## Features Clave
- **Monitoreo Real-Time**: Fetch probs cada 15s via Gamma API (agentes).
- **Trading Automático**: Book profit (≥85%), hedge (buy opposite), cut loss (≤78%).
- **Hedging Inteligente**: Math garantiza profit locked (e.g., post-hedge: siempre +$62 sin importar outcome).
- **AI Layer**: Prompt LLM (OpenAI/Grok) para ajustar thresholds (e.g., "BTC ETF news? Sube take-profit a 87%").
- **Risk Controls**: Max slippage 2%, min liquidity check, position sizing ≤$1000.
- **UX Simple**: CLI via agents + optional Streamlit dashboard (connect wallet, live PnL).

## User Journey (Ejemplo)
1. **Setup**: `pip install -r requirements.txt`, fundea testnet USDC, `python main.py --market btc-below-90k`.
2. **Inicial**: Agente compra 1250 YES shares ($1000 @0.80).
3. **Monitoreo**: Log: "Prob: 82% – Hold".
4. **Profit Trigger**: Prob 86% → "Booking $62 profit... Hedging with 413 NO shares @0.14".
5. **AI Alert**: Si news: "LLM: Baja threshold a 80% por FUD en X".
6. **Exit**: Prob 76% → "Cut loss: -$37 realized".

## Tech Highlights
- **Base**: Polymarket/agents (Gamma para data, Polymarket.py para orders).
- **AI**: RAG con Chroma (vectoriza news) + prompts en cli.py.
- **Seguro**: Testnet only, signed tx via web3, state en JSON.
- **Testeado**: 3 escenarios con historical data (FinFeed/Bitquery).

## Valor para heyelsa.ai
- **Producción-Ready**: Dockerizable, loggeado, escalable a multi-mercado.
- **Innovación**: Combina rules + AI para "smart hedging" – no solo bot, sino agente adaptativo.
- **Riesgos Cubiertos**: Slippage, gas, oracle delays (WebSocket + backups).

## Roadmap Post-MVP
- Full LLM (Grok-3 para sentiment en X).
- Multi-chain (Optimism integration).
- Dashboard web (React + WalletConnect).