# CONTEXT.MD – Polymarket Hedge Agent (Entrevista heyelsa.ai)

## Objetivo del MVP
Construir un agente autónomo que:
- Monitorea en tiempo real un mercado Polymarket (ej: "Will Bitcoin go below 90k before Dec 31?")
- Entrada inicial: $1000 en "Yes" cuando probabilidad ≈80%
- Si probabilidad sube ≥85% → vende 50–100% de Yes y usa la ganancia para comprar "No" (hedge)
- Si probabilidad baja ≤78% → vende todo Yes y sale
- Todo automatizado, seguro y con test report

## Stack obligatorio
- Python 3.11+
- Polymarket Python SDK (o py-clob-client)
- web3.py (Polygon Mainnet o Amoy testnet)
- Polygon RPC (Alchemy/Infura/QuickNode)
- .env para PRIVATE_KEY y RPC_URL
- Logging + tabla de test en Markdown

## Mercado de ejemplo (hardcodeado está OK)
Slug: will-bitcoin-go-below-90k-before-31-december-2025
Condition ID: 0x9c8... (lo buscamos en Polymarket o Bitquery)

## Funciones mínimas requeridas
1. get_current_probabilities(market_slug or condition_id)
2. get_position() → dict con yes_shares, no_shares, avg_cost
3. place_order(outcome_index: 0|1, amount_shares, price_limit=None)
4. book_profit_and_hedge()
5. cut_loss_and_exit()
6. main loop cada 15–30 segundos

## Test scenarios obligatorios (3)
1. Sube de 80% → 86% → book + hedge → PnL locked
2. Baja de 80% → 76% → stop loss → salida con pequeña pérdida
3. Sube a 85%, hedgea, luego baja a 60% → ganancia protegida

## Entregables finales
- Repo GitHub
- README.md con setup y cómo correr
- ARCHITECTURE.md
- tests/report.md con tablas
- (Opcional) streamlit_app.py con dashboard