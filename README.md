# Polymarket AI Hedge Agent

Automated trading and rebalancing agent for Polymarket prediction markets using a profit-locking hedging strategy.

## Overview

This agent monitors Polymarket probabilities in real-time and automatically:
- **Takes profit** when probability rises above threshold (85%) by selling YES shares and hedging with NO shares
- **Cuts losses** when probability falls below threshold (78%) by exiting the position
- **Locks in gains** through mathematical hedging that guarantees profit regardless of final outcome

## Features

- ✅ Real-time market monitoring via Polymarket SDK
- ✅ Web3 wallet integration (Polygon)
- ✅ Automated profit-taking and stop-loss execution
- ✅ Position state persistence
- ✅ Detailed logging with Rich CLI interface
- ✅ Comprehensive test scenarios and backtesting
- ✅ PnL tracking (unrealized and locked)

## Setup

### Prerequisites

- Python 3.9+
- Polygon wallet with USDC
- Polymarket API credentials

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
PRIVATE_KEY=your_private_key_without_0x
WALLET_ADDRESS=your_wallet_address
POLYMARKET_API_KEY=your_api_key
POLYMARKET_SECRET=your_secret
POLYMARKET_PASSPHRASE=your_passphrase
MARKET_SLUG=your-market-slug
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
python tests/backtest.py
```

## Strategy Logic

1. **Monitor**: Poll market every 15 seconds for current probability
2. **Evaluate**: Check if probability crosses take-profit (≥85%) or stop-loss (≤78%) thresholds
3. **Execute**:
   - **Take Profit**: Sell 60% YES shares → Buy NO shares with proceeds → Lock profit
   - **Stop Loss**: Sell all shares → Exit position → Minimize loss
4. **Track**: Update position state and calculate PnL

## Architecture

```
/agent         - Core strategy and position management
/api           - Polymarket API integration
/wallet        - Web3 wallet operations
/tests         - Test scenarios and backtesting
/utils         - Helper functions
/docs          - Documentation and reports
main.py        - Main execution loop
```

## Example Output

```
┏━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Time      ┃ Prob      ┃ Action    ┃ PnL       ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━┩
│ 10:00:00  │ 82.5%     │ HOLD      │ +$5.20    │
│ 10:05:15  │ 86.1%     │ HEDGE     │ +$12.40   │
│ 10:10:30  │ 84.3%     │ HOLD      │ +$11.80   │
└───────────┴───────────┴───────────┴───────────┘
```

## Testing

See [tests/report.md](tests/report.md) for detailed test scenarios:
- Scenario 1: Profit-taking and hedging
- Scenario 2: Stop-loss execution
- Scenario 3: Locked profit protection

## Documentation

- [CONTEXT.md](CONTEXT.md) - Business logic and strategy details
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture
- [tests/report.md](tests/report.md) - Test results and scenarios

## License

MIT

## Disclaimer

This is educational software. Use at your own risk. Always test with small amounts first.
