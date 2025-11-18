# To-Do List por Fases – Polymarket AI Hedge Agent
## Deadline: 21 nov 2025 23:59

### FASE 0 – Setup inicial (30–60 min)
- [ ] Crear repo GitHub (público o privado + invitame si querés: @natalan)
- [ ] Crear carpetas: `/agent`, `/api`, `/wallet`, `/tests`, `/docs`, `/utils`
- [ ] Crear archivos base:
  - `requirements.txt`
  - `.env.example`
  - `.gitignore`
  - `CONTEXT.md` 
  - `README.md`
- [ ] Commit inicial: “chore: initial project setup”

### FASE 1 – Conexión a Polymarket + Wallet (2–4 horas)
- [ ] Instalar y probar Polymarket SDK o py-clob-client
- [ ] Configurar web3.py con Polygon (Amoy testnet o Mainnet)
- [ ] Función: conectar wallet desde PRIVATE_KEY (.env)
- [ ] Función: `get_market_data(condition_id or slug)` → devuelve yes_price, no_price, volume
- [ ] Función: `get_current_probabilities()` → devuelve float 0.XX para Yes
- [ ] Probar en consola que traes precios reales cada 10 segundos

### FASE 2 – Position Manager & Estado (2–3 horas)
- [ ] Clase `Position` con atributos:
  - yes_shares, no_shares
  - avg_cost_yes, avg_cost_no
  - entry_prob, current_pnl, locked_pnl
- [ ] Función: cargar posición desde archivo JSON o DB simple (`position.json`)
- [ ] Función: guardar posición después de cada trade
- [ ] Función: calcular PnL unrealized y locked

### FASE 3 – Core Strategy (la que te evalúan – 4–6 horas)
- [ ] `should_take_profit(current_prob)` → retorna True si ≥85% (configurable)
- [ ] `should_cut_loss(current_prob)` → retorna True si ≤78% (configurable)
- [ ] `book_profit_and_rebalance()`
  - Vender 60–100% de Yes shares
  - Con el cash obtenido → comprar máximo No shares posible
  - Log: “Profit booked + hedged”
- [ ] `cut_loss_and_exit()`
  - Vender 100% Yes shares (y No si hubiera)
  - Log: “Stop-loss triggered – position closed”
- [ ] Matemática exacta de hedging (garantizar profit sin importar outcome)

### FASE 4 – Main Loop & Automation (1–2 horas)
- [ ] `main.py` con loop infinito:
  ```python
  while True:
      prob = get_current_probabilities()
      log_current_status()
      if should_take_profit(prob):
          book_profit_and_rebalance()
      elif should_cut_loss(prob):
          cut_loss_and_exit()
      time.sleep(15)
  ```
- [ ] Logging rico (rich library) con colores y tabla en tiempo real
- [ ] Manejo de excepciones + reconnect WebSocket/RPC

### FASE 5 – Tests & Report (3–4 horas – OBLIGATORIO)
- [ ] Crear `/tests/report.md`
- [ ] Simular mínimo 3 escenarios completos:
  - Sube 80% → 86% → hedgea → ganancia protegida
  - Baja 80% → 76% → stop-loss → salida con pérdida mínima
  - Sube a 85%, hedgea, luego baja a 50% → ganancia locked
- [ ] Cada escenario con tabla Markdown (tiempo, prob, acción, shares, cash, PnL)
- [ ] Bonus: script `backtest.py` que corre los 3 escenarios sin tocar blockchain

### FASE 6 – Polish & Entregables finales (2–3 horas)
- [ ] Completar `README.md`:
  - Título + descripción
  - Setup paso a paso
  - Cómo correr
  - Ejemplo de log
- [ ] Crear `ARCHITECTURE.md` con diagrama simple (texto o mermaid)
- [ ] (Opcional pero mata) `streamlit_app.py` con:
  - Botón Connect Wallet (WalletConnect o directo)
  - Tabla en vivo de posición y PnL
  - Gráfico de probabilidad
- [ ] Video corto 2–3 min (Loom) corriendo el agente en tiempo real
- [ ] Tag final: `v1.0.0-mvp`

### FASE 7 – Submit
- [ ] Enviar proyecto final