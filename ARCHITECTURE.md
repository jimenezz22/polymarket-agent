# Architecture - Polymarket AI Hedge Agent

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Main Loop                            │
│                        (main.py)                             │
└───────────┬─────────────────────────────────────┬───────────┘
            │                                     │
            ▼                                     ▼
┌───────────────────────┐           ┌─────────────────────────┐
│   Market Data Layer   │           │    Strategy Engine      │
│      (/api)           │           │      (/agent)           │
│                       │           │                         │
│ - py-clob-client      │           │ - Position Manager      │
│ - Market prices       │           │ - PnL Calculator        │
│ - Probabilities       │           │ - Take Profit Logic     │
│ - Order execution     │           │ - Stop Loss Logic       │
└───────────┬───────────┘           │ - Hedging Math          │
            │                       └──────────┬──────────────┘
            │                                  │
            ▼                                  ▼
┌───────────────────────┐           ┌─────────────────────────┐
│    Wallet Layer       │           │    State Management     │
│     (/wallet)         │           │                         │
│                       │           │ - position.json         │
│ - web3.py             │           │ - Trade history         │
│ - Polygon RPC         │           │ - Persistent state      │
│ - Transaction signing │           └─────────────────────────┘
│ - Balance checking    │
└───────────────────────┘
```

## Component Details

### 1. Main Loop (`main.py`)

**Responsibilities:**
- Initialize wallet and API connections
- Run infinite monitoring loop
- Orchestrate strategy execution
- Handle errors and reconnections
- Logging and console output

**Flow:**
```python
while True:
    1. Fetch current market probability
    2. Load position state
    3. Calculate current PnL
    4. Evaluate strategy conditions
    5. Execute trades if needed
    6. Save updated state
    7. Log results
    8. Sleep for polling interval
```

### 2. Market Data Layer (`/api`)

**Files:**
- `polymarket_client.py` - Polymarket SDK wrapper
- `market_data.py` - Market data fetching and parsing

**Key Functions:**
- `get_market_by_condition_id(condition_id)` → Returns market info + tokens
- `get_yes_price(condition_id)` → Returns float (e.g. 0.86) - share price = implied probability
- `get_user_shares(address, condition_id)` → Returns (yes_shares, no_shares)
- `place_order(condition_id, outcome_index, amount_shares, price=None)` → price=None = market order with slippage protection

### 3. Wallet Layer (`/wallet`)

**Files:**
- `wallet_manager.py` - Web3 wallet operations

**Key Functions:**
- `connect_wallet(private_key)` → Initialize wallet from private key
- `get_balance(token_address)` → Get USDC balance
- `approve_token(token, spender, amount)` → ERC20 approval
- `sign_transaction(tx)` → Sign transaction with private key
- `get_address()` → Get wallet address

### 4. Strategy Engine (`/agent`)

**Files:**
- `position.py` - Position class and management
- `strategy.py` - Core trading logic
- `pnl_calculator.py` - PnL computation

**Position Class:**
```python
class Position:
    yes_shares: float
    no_shares: float
    avg_cost_yes: float
    avg_cost_no: float
    entry_prob: float

    def calculate_unrealized_pnl(current_prob)
    def calculate_locked_pnl()
    def update_from_trade(side, shares, price)
    def save()
    def load()
```

**Strategy Functions:**
- `should_take_profit(current_prob, threshold)` → bool
- `should_cut_loss(current_prob, threshold)` → bool
- `book_profit_and_rebalance(position, sell_pct)` → Execute hedge
- `cut_loss_and_exit(position)` → Exit position
- `calculate_hedge_amount(position, sell_proceeds)` → Hedge math

### 5. Utilities (`/utils`)

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

Environment variables (`.env`):
```
# Core
PRIVATE_KEY=0x...
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/xxx
CHAIN_ID=137  # or 80002 for Amoy testnet

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
