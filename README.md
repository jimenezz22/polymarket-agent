# Polymarket AI Hedge Agent

> **Built on top of [Polymarket/agents](https://github.com/Polymarket/agents) framework**

Automated trading and rebalancing agent for Polymarket prediction markets using a profit-locking hedging strategy with AI-driven decision making.

## Overview

This agent extends the official Polymarket Agents framework with a sophisticated hedging strategy that:
- **Takes profit** when probability rises above threshold (85%) by selling YES shares and hedging with NO shares
- **Cuts losses** when probability falls below threshold (78%) by exiting the position
- **Locks in gains** through mathematical hedging that guarantees profit regardless of final outcome
- **AI-enhanced decisions** (optional) using LLM to adjust thresholds based on news/sentiment

## Features

- ✅ Real-time market monitoring via Polymarket Gamma API
- ✅ Integration with official Polymarket Agents framework
- ✅ Automated profit-taking and stop-loss execution
- ✅ Mathematical hedging for guaranteed profit locking
- ✅ Position state persistence
- ✅ Detailed logging with Rich CLI interface
- ✅ Comprehensive test scenarios and backtesting
- ✅ PnL tracking (unrealized and locked)
- ✅ AI/LLM integration for dynamic threshold adjustment

## Architecture

This project uses the Polymarket Agents framework and extends it with custom hedging logic:

```
polymarket-agent/
├── agents/              # Official Polymarket Agents framework
│   ├── polymarket/      # Gamma API & trading clients
│   ├── application/     # Trade execution engine
│   └── connectors/      # News, search, RAG integrations
├── my_agent/            # Custom hedging strategy (our code)
│   ├── strategy.py      # Take-profit & stop-loss logic
│   ├── position.py      # Position management
│   └── pnl_calculator.py # PnL math & hedging calculations
├── utils/               # Utilities (config, logging, helpers)
├── docs/                # Documentation
└── main.py              # Main execution loop
```

## Setup

### Prerequisites

- Python 3.9+
- Polygon wallet with USDC
- Polymarket API access (optional for live trading)

### Installation

```bash
# Clone repository
git clone <repo-url>
cd polymarket-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Configuration

Edit `.env` file:

```env
# Required for Polymarket Agents
POLYGON_WALLET_PRIVATE_KEY=your_private_key_without_0x
GOOGLE_API_KEY=your_google_api_key  # for AI features

# Network
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/xxx
CHAIN_ID=137  # or 80002 for Amoy testnet

# Market
MARKET_CONDITION_ID=0x9c8f9e...  # Polymarket condition ID

# Strategy
TAKE_PROFIT_PROBABILITY=0.85
STOP_LOSS_PROBABILITY=0.78
HEDGE_SELL_PERCENT=1.0  # Recommended: sell 100% for maximum hedge
POLL_INTERVAL_SECONDS=20
```

## Usage

### Run the Agent

```bash
python main.py
```

### Run Tests

```bash
pytest tests/
```

### Run Backtest Scenarios

```bash
python test_strategy.py
```

### Use Official Polymarket Agents CLI

```bash
# Get markets
python scripts/python/cli.py get-all-markets --limit 10

# Execute official trade script
python agents/application/trade.py
```

## Strategy Logic

1. **Monitor**: Poll market every 15-20 seconds for current probability
2. **Evaluate**: Check if probability crosses take-profit (≥85%) or stop-loss (≤78%) thresholds
3. **Execute**:
   - **Take Profit**: Sell YES shares → Buy NO shares with proceeds → Lock profit
   - **Stop Loss**: Sell all shares → Exit position → Minimize loss
4. **Track**: Update position state and calculate PnL

### Hedging Math Example

```
Entry: 1250 YES @ $0.80 = $1000 invested

Price rises to 86% (TAKE PROFIT):
  Sell: 1250 YES @ $0.86 = $1,075
  Buy: 7,679 NO @ $0.14 = $1,075

Final outcomes:
  If YES wins: 0 * $1 = $0
  If NO wins: 7,679 * $1 = $7,679

Guaranteed profit: $7,679 - $1,000 = +$6,679 (if NO wins)
```

## Testing

See test_strategy.py for detailed test scenarios:
- **Scenario 1**: Profit-taking and hedging (80% → 86%)
- **Scenario 2**: Stop-loss execution (80% → 76%)
- **Scenario 3**: Locked profit protection (85% → hedge → 50% crash)

## Documentation

### Core Docs
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design & components
- [TRADING_LOGIC.md](docs/TRADING_LOGIC.md) - Strategy & hedge math
- [API_USAGE.md](docs/API_USAGE.md) - Polymarket & Gemini APIs
- [SECURITY.md](docs/SECURITY.md) - Wallet & transaction security
- [TESTING.md](docs/TESTING.md) - Test results & coverage

### Additional
- [FUTURE.md](docs/FUTURE.md) - Roadmap & improvements
- [REFACTORING_REPORT.md](docs/REFACTORING_REPORT.md) - Clean code refactoring details

## Related Repos

- [Polymarket/agents](https://github.com/Polymarket/agents) - Official framework we extend
- [py-clob-client](https://github.com/Polymarket/py-clob-client) - Python client for Polymarket CLOB
- [python-order-utils](https://github.com/Polymarket/python-order-utils) - Order signing utilities

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

MIT

## Disclaimer

This is educational software. Use at your own risk. Always test with small amounts first. Trading on Polymarket is subject to their [Terms of Service](https://polymarket.com/tos).

## Contact

For questions about the hedging strategy or AI integration, open an issue in this repository.

For questions about the base Polymarket Agents framework, see the [official agents repo](https://github.com/Polymarket/agents).
