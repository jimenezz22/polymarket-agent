# Installation Guide - Polymarket AI Hedge Agent

## Quick Start (Recommended)

### 1. Run Automated Setup

```bash
./setup.sh
```

This script will:
- ✓ Check Python 3.9+ is installed
- ✓ Create/verify virtual environment
- ✓ Install all dependencies from requirements.txt
- ✓ Verify imports work correctly
- ✓ Create .env from template

### 2. Configure Environment

Edit the `.env` file with your credentials:

```bash
nano .env  # or use your preferred editor
```

Required variables:
```env
POLYGON_WALLET_PRIVATE_KEY=your_private_key_here
MARKET_CONDITION_ID=0x...  # Your target market
```

Optional variables:
```env
OPENAI_API_KEY=sk-...  # For AI features
TAKE_PROFIT_PROBABILITY=0.85
STOP_LOSS_PROBABILITY=0.78
```

### 3. Run the Agent

```bash
source venv/bin/activate
python main.py
```

---

## Manual Installation

If you prefer manual installation:

### Step 1: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure

```bash
cp .env.example .env
# Edit .env with your credentials
```

### Step 4: Verify Installation

```bash
python3 -c "from my_agent import Position, TradingStrategy; print('✓ Installation successful')"
```

---

## Dependency List

This project uses verified packages from:
- **Polymarket Official**: `py_clob_client`, `py_order_utils`
- **Web3**: `web3`, `eth-account`
- **Data**: `pandas`, `numpy`, `httpx`
- **AI/LLM**: `openai`, `langchain`, `chromadb` (optional)
- **CLI**: `rich`, `typer`, `python-dotenv`
- **Testing**: `pytest`, `pytest-asyncio`

Full list in [requirements.txt](requirements.txt)

---

## Troubleshooting

### Import Errors

If you get `ModuleNotFoundError`:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Web3 Middleware Error

If you see `cannot import name 'geth_poa_middleware'`:

```bash
pip install --upgrade web3
```

### Permission Denied on setup.sh

```bash
chmod +x setup.sh
./setup.sh
```

### Python Version Issues

Ensure you have Python 3.9+:

```bash
python3 --version
```

If not, install from [python.org](https://www.python.org/downloads/)

---

## Testing Installation

### Test Custom Modules

```bash
python3 << EOF
from my_agent import Position, TradingStrategy
from my_agent.pnl_calculator import calculate_hedge_shares

# Test hedge calculation
yes, no, proceeds = calculate_hedge_shares(1250, 1.0, 0.86, 0.14)
print(f"✓ Hedge: {yes:.0f} YES → {no:.0f} NO")
EOF
```

### Test Agents Framework

```bash
python3 << EOF
from agents.polymarket.gamma import GammaMarketClient
gamma = GammaMarketClient()
print(f"✓ Gamma client: {gamma.gamma_url}")
EOF
```

### Test Full Integration

```bash
python main.py --help  # Should show usage info
```

---

## Next Steps

After installation:

1. **Read Documentation**
   - [README.md](README.md) - Project overview
   - [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details
   - [docs/product.md](docs/product.md) - Strategy explanation

2. **Test on Testnet First**
   - Use Polygon Amoy testnet (CHAIN_ID=80002)
   - Get test USDC from faucet
   - Test with small amounts

3. **Run Tests**
   ```bash
   pytest tests/
   python my_agent/tests_legacy/test_strategy.py
   ```

4. **Use Official CLI**
   ```bash
   python scripts/python/cli.py get-all-markets --limit 10
   ```

---

## Support

- **Issues**: Open an issue on GitHub
- **Framework**: See [Polymarket/agents](https://github.com/Polymarket/agents)
- **API Docs**: [Polymarket API](https://docs.polymarket.com)

---

## Security Notes

⚠️ **IMPORTANT**:
- Never commit `.env` file
- Use testnet for initial testing
- Keep private keys secure
- Start with small amounts
- Review all trades in demo mode first

---

## Uninstalling

To remove the project:

```bash
# Deactivate venv
deactivate

# Remove virtual environment
rm -rf venv/

# Remove dependencies
pip uninstall -r requirements.txt -y
```
