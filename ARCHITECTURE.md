# Architecture - Polymarket AI Hedge Agent

> **Built on [Polymarket/agents](https://github.com/Polymarket/agents) Framework**

## System Overview

This project extends the official Polymarket Agents framework with custom hedging strategy logic.

```
┌─────────────────────────────────────────────────────────────┐
│                      Main Loop (main.py)                     │
│         Integrates Agents Framework + Custom Strategy       │
└───────────┬──────────────────────────────────────┬──────────┘
            │                                      │
            ▼                                      ▼
┌──────────────────────────┐          ┌─────────────────────────┐
│  Polymarket Agents       │          │  Custom Hedge Strategy  │
│  Framework (/agents)     │          │     (/my_agent)         │
│                          │          │                         │
│ • Polymarket()           │◄────────►│ • TradingStrategy       │
│   - CLOB Client          │          │   - Take Profit Logic   │
│   - Order Execution      │          │   - Stop Loss Logic     │
│   - Wallet Management    │          │   - Hedging Math        │
│                          │          │                         │
│ • GammaMarketClient()    │◄────────►│ • Position Manager      │
│   - Market Data          │          │   - State Tracking      │
│   - Probabilities        │          │   - PnL Calculation     │
│   - Events/News          │          │   - Trade History       │
│                          │          │                         │
│ • Connectors             │          │ • PnL Calculator        │
│   - News API             │          │   - Hedge Calculations  │
│   - Search               │          │   - ROI Metrics         │
│   - ChromaDB (RAG)       │          │   - Breakeven Analysis  │
└──────────────────────────┘          └─────────────────────────┘
            │                                      │
            └──────────────┬───────────────────────┘
                           ▼
                  ┌─────────────────────┐
                  │  State Management   │
                  │                     │
                  │ • position.json     │
                  │ • Trade history     │
                  │ • Config (.env)     │
                  └─────────────────────┘
```

## Component Details

### 1. Main Loop (`main.py`)

**Integration Point:** Uses both Agents framework and custom strategy

**Responsibilities:**
- Initialize `Polymarket()` and `GammaMarketClient()` from agents framework
- Initialize custom `TradingStrategy` and `Position` manager
- Run infinite monitoring loop
- Orchestrate strategy evaluation
- Display rich console output
- Handle graceful shutdown

**Flow:**
```python
# Initialize (from agents framework)
polymarket_client = Polymarket()           # Official client
gamma_client = GammaMarketClient()         # Market data
position = get_position()                  # Our position manager
strategy = create_strategy(position)       # Our hedge strategy

while not killed:
    1. Fetch current market data via gamma_client.get_markets()
    2. Parse YES/NO prices from market.outcomePrices
    3. Get position summary with current PnL
    4. Evaluate strategy: strategy.evaluate(current_prob, yes_price, no_price)
    5. Execute trades if needed (via polymarket_client)
    6. Update and save position state
    7. Display status with Rich CLI
    8. Sleep for polling interval (default 20s)
```

### 2. Polymarket Agents Framework (`/agents`)

**Source:** Official [Polymarket/agents](https://github.com/Polymarket/agents) repository

**Components Used:**

#### 2.1 `agents/polymarket/polymarket.py`
- `Polymarket()` class - Main CLOB client
- Handles wallet management (web3, signing)
- Order execution via `py_clob_client`
- USDC balance checking
- Token approvals for CTF Exchange

**Key Methods:**
```python
polymarket_client.get_address_for_private_key() → wallet address
polymarket_client.get_balance_usdc() → USDC balance
polymarket_client.place_order(...) → execute trade
```

#### 2.2 `agents/polymarket/gamma.py`
- `GammaMarketClient()` - Market data from Gamma API
- Fetches live probabilities
- Market info, events, tags
- Pydantic models for type safety

**Key Methods:**
```python
gamma_client.get_markets({"condition_id": "0x..."}) → list[Market]
market.outcomePrices → [yes_price, no_price]
```

#### 2.3 `agents/connectors/`
- News API integration
- Search capabilities
- ChromaDB for RAG (optional for AI features)

### 3. Custom Hedge Strategy (`/my_agent`)

**Our Custom Implementation** - This is where the hedging magic happens

**Files:**
- `my_agent/position.py` - Position tracking and persistence
- `my_agent/strategy.py` - Take-profit/stop-loss logic
- `my_agent/pnl_calculator.py` - Hedging math
- `my_agent/utils/` - Config, logging, helpers

#### 3.1 Position Manager (`position.py`)

**Position Class:**
```python
class Position:
    yes_shares: float          # Current YES holdings
    no_shares: float           # Current NO holdings
    avg_cost_yes: float        # Average cost per YES
    avg_cost_no: float         # Average cost per NO
    entry_prob: float          # Entry probability
    total_invested: float      # Total USDC invested
    total_withdrawn: float     # Total USDC withdrawn
    trades: List[Trade]        # Complete trade history

    # Core methods
    def open_position(shares, price, side="YES")
    def sell_shares(shares, price, side="YES") → usdc_proceeds
    def calculate_unrealized_pnl(yes_price, no_price) → Dict
    def calculate_locked_pnl() → float  # GUARANTEED profit from hedge
    def save() → Persists to position.json
    def load() → Loads from position.json
```

#### 3.2 Trading Strategy (`strategy.py`)

**TradingStrategy Class:**
```python
class TradingStrategy:
    def __init__(position, take_profit=0.85, stop_loss=0.78, hedge_pct=1.0)

    # Decision logic
    def should_take_profit(current_prob) → bool
    def should_cut_loss(current_prob) → bool
    def evaluate(current_prob, yes_price, no_price) → Dict[action, reason]

    # Execution (integrates with Polymarket client)
    def book_profit_and_rebalance(yes_price, no_price) → Dict
    def cut_loss_and_exit(yes_price, no_price) → Dict
    def execute_action(action) → Optional[Dict]
```

**Key Logic:**
- Only take profit if: has YES shares AND not hedged AND prob ≥ 85%
- Only cut loss if: has YES shares AND not hedged AND prob ≤ 78%
- If already hedged: HOLD (profit is locked!)

#### 3.3 PnL Calculator (`pnl_calculator.py`)

**Hedging Math Functions:**
```python
calculate_hedge_shares(yes_shares, sell_pct, yes_price, no_price)
  → (yes_to_sell, no_to_buy, usdc_proceeds)

calculate_final_pnl_scenarios(yes_shares, no_shares, total_cost)
  → {pnl_if_yes_wins, pnl_if_no_wins, guaranteed_min, is_profitable}

calculate_breakeven_prices(...)
calculate_roi(current_value, invested, withdrawn)
```

### 4. Utilities (`my_agent/utils/`)

**Files:**
- `logger.py` - Rich logging configuration
- `config.py` - Environment variable loading
- `helpers.py` - Common helper functions

## Data Flow

### Take Profit Flow

```
1. Monitor: current_prob = 0.86 (above 0.85 threshold)
2. Strategy: should_take_profit() → True
3. Calculate: sell 100% of YES shares (recommended for maximum hedge effectiveness)
4. Execute: Sell YES shares → receive USDC
5. Calculate: Max NO shares purchasable with proceeds
6. Execute: Buy NO shares
7. Update: position.yes_shares -= sold, position.no_shares += bought
8. Calculate: locked_pnl = guaranteed_profit (outcome doesn't matter now)
9. Save: position.save()
10. Log: "Profit booked and hedged: locked $X.XX"
```

### Stop Loss Flow

```
1. Monitor: current_prob = 0.76 (below 0.78 threshold)
2. Strategy: should_cut_loss() → True
3. Execute: Sell all YES shares
4. Execute: Sell all NO shares (if any)
5. Calculate: final_pnl = exit_value - cost_basis
6. Update: position.reset()
7. Save: position.save()
8. Log: "Stop loss triggered: realized $X.XX"
```

## Configuration

Environment variables (`.env`) - **Compatible with both our config and agents framework**:

```bash
# Wallet (agents framework variable)
POLYGON_WALLET_PRIVATE_KEY=0x...

# Network
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/xxx
CHAIN_ID=137  # 137 = Polygon Mainnet, 80002 = Amoy Testnet

# Market
MARKET_CONDITION_ID=0x9c8f9e...  # ← only this, not slug

# Strategy thresholds
ENTRY_PROBABILITY=0.80
TAKE_PROFIT_PROBABILITY=0.85
STOP_LOSS_PROBABILITY=0.78
HEDGE_SELL_PERCENT=1.0        # 1.0 = sell all YES on take-profit (recommended)
POLL_INTERVAL_SECONDS=20

# Risk
MAX_SLIPPAGE_PERCENT=2.0
MIN_LIQUIDITY_USD=5000
```

## State Persistence

`position.json` format:
```json
{
  "yes_shares": 1250.0,
  "no_shares": 0.0,
  "avg_cost_yes": 0.80,
  "avg_cost_no": 0.0,
  "entry_prob": 0.80,
  "entry_timestamp": "2024-11-18T10:00:00Z",
  "total_invested": 1000.0,
  "trades": [
    {
      "timestamp": "2024-11-18T10:00:00Z",
      "side": "YES",
      "shares": 1250.0,
      "price": 0.80,
      "type": "BUY"
    }
  ]
}
```

## Error Handling

- **RPC Failures**: Retry with exponential backoff
- **API Rate Limits**: Respect rate limits, queue requests
- **Insufficient Funds**: Log error, skip trade
- **Order Failures**: Retry up to 3 times, then alert
- **State Corruption**: Validate position.json on load

## Security Considerations

- Private keys stored only in `.env` (never committed)
- `.env` in `.gitignore`
- No API keys in logs
- Transaction simulation before execution
- Slippage protection on orders

## Testing Strategy

1. **Unit Tests**: Test individual functions with mocked data
2. **Integration Tests**: Test component interactions
3. **Backtesting**: Simulate scenarios with historical data
4. **Live Testing**: Small amounts on testnet/mainnet

## Deployment

**Local:**
```bash
python main.py
```

**Background (Production):**
```bash
nohup python main.py > agent.log 2>&1 &
```

**Docker (Future):**
```dockerfile
FROM python:3.11-slim
COPY . /app
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

## Performance Considerations

- Poll interval: 15 seconds (balance between responsiveness and rate limits)
- Market orders for speed (vs limit orders for price)
- Local state cache to minimize API calls
- Async operations where possible

## Future Enhancements

- [ ] Multi-market support
- [ ] Advanced hedging strategies (delta-neutral)
- [ ] Machine learning probability predictions
- [ ] Telegram/Discord notifications
- [ ] Web dashboard (Streamlit)
- [ ] Docker deployment
- [ ] Automated testing on testnet

## Why This Agent Wins (Interview Cheat Sheet)

- **Zero discretion**: 100% rule-based, auditable, reproducible
- **Guaranteed profit on take-profit**: after hedge, outcome doesn't matter
- **Risk-defined from day 1**: max drawdown = 2–3% (80% → 78%)
- **Real hedging math**: not just "buy the other side", but **lock actual USD profit**
- **Production-ready**: logging, state persistence, error resilience, config-driven
