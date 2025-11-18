# Polymarket API Reference

Complete API documentation for building automated trading agents on Polymarket.

---

## Table of Contents

1. [Market Discovery & Data (Gamma API)](#1-market-discovery--data-gamma-api)
2. [Real-Time Prices & Probabilities (CLOB + Gamma)](#2-real-time-prices--probabilities-clob--gamma)
3. [Trade Execution & Rebalancing (CLOB API)](#3-trade-execution--rebalancing-clob-api)
4. [Positions & Risk Management (Data API)](#4-positions--risk-management-data-api)
5. [WebSocket Real-Time Feeds](#5-websocket-real-time-feeds)
6. [Authentication & Approvals](#6-authentication--approvals)

---

## 1. Market Discovery & Data (Gamma API)

Base URL: `https://gamma.api.polymarket.com`

### GET /markets

List all active markets (or filtered by slug/tag).

**Parameters:**
- `slug` (string): e.g., `"will-bitcoin-go-below-90k"`
- `tag_id` (int): Category filter (e.g., crypto)
- `active` (bool): `true` for active markets only
- `limit` (int): Max results (default 100)
- `cursor` (string): Pagination cursor

**Response:**
```json
{
  "markets": [
    {
      "slug": "will-bitcoin-go-below-90k",
      "condition_id": "0x9c8f...",
      "tokens": [
        {
          "token_id": "0xabc...",
          "outcome": "Yes",
          "price_usd": 0.80
        }
      ],
      "volume": 1000000,
      "liquidity": 50000
    }
  ]
}
```

**Use in Agent:**
- Initialize position
- Get `condition_id` and `token_id`
- Filter by `end_date` for live markets

**Python SDK Example:**
```python
from py_clob_client.client import ClobClient

client = ClobClient(host="https://gamma.api.polymarket.com")
markets = client.get_markets(slug="will-bitcoin-go-below-90k")
condition_id = markets[0]["condition_id"]
```

---

### GET /events

Markets grouped by event (more efficient for discovery).

**Parameters:**
- `tag_id` (int): e.g., crypto tags
- `limit` (int): Default 50

**Response:**
Similar to `/markets`, but with `event_id` and embedded markets.

**Use in Agent:**
- For backtesting: fetch historical via `historical=true`

---

### GET /tags

Get available categories (e.g., "bitcoin", "crypto").

**Parameters:** None

**Response:**
```json
{
  "tags": [
    {
      "id": 123,
      "name": "Bitcoin",
      "image": "url"
    }
  ]
}
```

**Use in Agent:**
- Filter markets with `?tag_id=123`

---

## 2. Real-Time Prices & Probabilities (CLOB + Gamma)

### GET /prices

Current price snapshot for tokens/markets.

**Parameters:**
- `token_id` (string): From `/markets`
- `currency` (string): `USD`

**Response:**
```json
{
  "prices": [
    {
      "token_id": "0xabc",
      "price": 0.85,
      "volume_24h": 5000
    }
  ]
}
```

**Use in Agent:**
- `prob_yes = price`
- Threshold check: `if price > 0.85 → book_profit()`

---

### GET /historical/prices

OHLCV historical data for backtesting.

**Parameters:**
- `token_id` (string)
- `start_date` (ISO): `2025-11-01T00:00:00Z`
- `end_date` (ISO)
- `interval` (string): `1h`, `1d`

**Response:**
```json
{
  "historical": [
    {
      "timestamp": "2025-11-18T10:00",
      "open": 0.80,
      "high": 0.86,
      "low": 0.78,
      "close": 0.85,
      "volume": 1000
    }
  ]
}
```

**Use in Agent:**
- For test report: simulate probability movements

---

### GET /book (or /books)

Order book (bids/asks) for a token.

**Parameters:**
- `token_id` (string)
- `level` (int): `2` for market depth

**Response:**
```json
{
  "bids": [
    [0.84, 100],
    [0.83, 50]
  ],
  "asks": [
    [0.86, 200]
  ]
}
```

**Use in Agent:**
- Calculate slippage for hedging
- New in 2025: includes market metadata

---

### GET /last-trade

Last trade price for a token.

**Parameters:**
- `token_id` (string)

**Response:**
```json
{
  "price": 0.85,
  "timestamp": "2025-11-18T10:05"
}
```

**Use in Agent:**
- Confirm probabilities in monitoring loop

**Python SDK Example:**
```python
last_price = client.get_last_trade_price(token_id="0xabc-yes")
prob = last_price  # Direct float for threshold
```

---

## 3. Trade Execution & Rebalancing (CLOB API)

Base URL: `https://clob.polymarket.com`

### POST /orders

Create order (limit or market).

**Headers:**
```
Authorization: Bearer {api_key}
Content-Type: application/json
```

**Body:**
```json
{
  "token_id": "0xabc",
  "price": 0.85,
  "size": 1250,
  "side": "SELL",
  "type": "GTC",
  "signature": "0x..."
}
```

**Response:**
```json
{
  "order_id": "0x123",
  "status": "filled"
}
```

**Use in Agent:**
- Sell 50-100% YES when prob rises → use proceeds to buy NO
- Batch up to 15 orders (new in 2025)

**Python SDK Example:**
```python
order = OrderArgs(
    token_id="yes-token",
    price=0.85,
    size=625,
    side="SELL"
)
signed_order = client.create_order(order)
resp = client.post_order(signed_order)
```

---

### POST /market-orders

Market order (fill-or-kill).

**Body:**
Similar to `/orders`, but `order_type: "FOK"`

**Use in Agent:**
- Fast execution in hedging
- Avoid slippage > 2%

---

### GET /trades

Trade history (your trades or global).

**Parameters:**
- `user_address` (string)
- `market_token_id` (string)
- `limit` (int): Default 100

**Response:**
```json
{
  "trades": [
    {
      "timestamp": "2025-11-18",
      "side": "BUY",
      "price": 0.80,
      "size": 1250,
      "pnl": 62.5
    }
  ]
}
```

**Use in Agent:**
- Track PnL post-rebalance

---

### POST /auth/api-key

Generate/derive API key for authentication.

**Body:**
```json
{
  "address": "0x...",
  "nonce": 123456,
  "signature": "0x..."
}
```

**Response:**
```json
{
  "api_key": "abc123",
  "passphrase": "secret"
}
```

**Use in Agent:**
- Required for all POST operations
- Use in headers: `Authorization: Bearer {api_key}`

---

## 4. Positions & Risk Management (Data API)

### GET /holdings

User positions (YES/NO shares).

**Parameters:**
- `address` (string): User wallet address

**Response:**
```json
{
  "holdings": [
    {
      "token_id": "yes",
      "amount": 1250,
      "value_usd": 1062.5
    }
  ]
}
```

**Use in Agent:**
- Calculate unrealized PnL: `(current_price * shares) - cost_basis`

---

### GET /value

Total value of holdings.

**Parameters:**
- `address` (string)

**Response:**
```json
{
  "total_value_usd": 1156.25,
  "locked_pnl": 531
}
```

**Use in Agent:**
- Verify hedge: if both YES and NO > 0 → profit locked

---

### GET /holders

Top holders of a market.

**Parameters:**
- `condition_id` (string)

**Response:**
```json
{
  "holders": [
    {
      "address": "0x...",
      "shares_yes": 10000
    }
  ]
}
```

**Use in Agent:**
- Optional: detect whale activity for risk management

---

## 5. WebSocket Real-Time Feeds

**WebSocket URL:** `wss://clob.polymarket.com/ws`

### Subscribe to Prices

**Send:**
```json
{
  "action": "subscribe",
  "channel": "prices",
  "token_id": "0xabc"
}
```

**Receive:**
```json
{
  "type": "price_update",
  "price": 0.86
}
```

**Available Channels:**
- `prices` - Price updates (~2s/block on Polygon)
- `trades` - Trade executions
- `orders` - Order book changes
- `markets` - Market metadata updates

**Use in Agent:**
- Replace polling with WebSocket for real-time monitoring
- Lower latency for threshold triggers

---

## 6. Authentication & Approvals

### On-Chain Approvals (Before Trading)

**Required:** Approve USDC to exchange contract

**Python SDK Example:**
```python
# Approve USDC (one-time, or when allowance runs low)
client.approve_token(
    token_id="USDC",
    amount=10**6  # $1000 in USDC (6 decimals)
)
```

**Web3.py Direct:**
```python
from web3 import Web3

usdc_contract = w3.eth.contract(address=USDC_ADDRESS, abi=ERC20_ABI)
tx = usdc_contract.functions.approve(
    EXCHANGE_ADDRESS,
    2**256 - 1  # Infinite approval
).build_transaction({
    'from': wallet_address,
    'nonce': w3.eth.get_transaction_count(wallet_address)
})

signed_tx = w3.eth.account.sign_transaction(tx, private_key)
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
```

---

## Agent Implementation Flow

### 1. Initialize

```python
from py_clob_client.client import ClobClient

# Read-only client (no auth)
client = ClobClient(host="https://gamma.api.polymarket.com")

# Authenticated client (for trading)
auth_client = ClobClient(
    host="https://clob.polymarket.com",
    key=PRIVATE_KEY,
    chain_id=137
)
```

### 2. Discovery

```python
markets = client.get_markets(slug="your-market-slug")
condition_id = markets[0]["condition_id"]
token_id_yes = markets[0]["tokens"][0]["token_id"]
token_id_no = markets[0]["tokens"][1]["token_id"]
```

### 3. Monitoring Loop

```python
while True:
    # Get current price (prob)
    price = client.get_last_trade_price(token_id=token_id_yes)
    prob = float(price)

    # Check thresholds
    if prob >= 0.85:
        book_profit_and_hedge()
    elif prob <= 0.78:
        cut_loss_and_exit()

    time.sleep(15)
```

### 4. Execute Trade

```python
# Take profit: Sell YES
sell_order = OrderArgs(
    token_id=token_id_yes,
    price=None,  # Market order
    size=yes_shares * 0.60,  # Sell 60%
    side="SELL"
)
signed = auth_client.create_order(sell_order)
result = auth_client.post_order(signed)

# Calculate proceeds
proceeds_usdc = result["filled_size"] * result["avg_price"]

# Hedge: Buy NO with proceeds
buy_no_shares = proceeds_usdc / current_no_price
buy_order = OrderArgs(
    token_id=token_id_no,
    price=None,
    size=buy_no_shares,
    side="BUY"
)
auth_client.post_order(auth_client.create_order(buy_order))
```

### 5. Track Positions

```python
holdings = client.get_holdings(address=wallet_address)
yes_shares = next(h["amount"] for h in holdings if h["token_id"] == token_id_yes)
no_shares = next(h["amount"] for h in holdings if h["token_id"] == token_id_no)

# Calculate locked PnL
locked_pnl = min(yes_shares, no_shares) - total_invested
```

---

## Best Practices

1. **Rate Limits:** Cache prices locally, use WebSocket for real-time
2. **Slippage:** Use limit orders with `max_slippage=2%` for large trades
3. **Approvals:** Check allowance before each trade
4. **Error Handling:** Retry failed orders up to 3 times with exponential backoff
5. **Testing:** Use Polygon Amoy testnet first (chain_id=80002)
6. **Batch Orders:** 2025 update allows up to 15 orders per batch request

---

## Resources

- **Official Docs:** https://docs.polymarket.com
- **Python SDK:** `pip install py-clob-client`
- **GitHub Examples:** https://github.com/Polymarket/py-clob-client
- **API Status:** https://status.polymarket.com
- **Discord:** https://discord.gg/polymarket

---

## Updates (2025)

- ✅ Batch orders up to 15
- ✅ Enhanced `/book` endpoint with metadata
- ✅ WebSocket rate increased to ~2s/block
- ✅ New `historical=true` parameter for backtesting
