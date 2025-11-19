"""Configuration management for the Polymarket Agent."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # Core - Support both our var and agents framework var
    PRIVATE_KEY: str = os.getenv("PRIVATE_KEY") or os.getenv("POLYGON_WALLET_PRIVATE_KEY", "")
    POLYGON_RPC_URL: str = os.getenv(
        "POLYGON_RPC_URL",
        "https://polygon-mainnet.g.alchemy.com/v2/demo"
    )
    CHAIN_ID: int = int(os.getenv("CHAIN_ID", "137"))

    # OpenAI for AI features (optional)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Market
    MARKET_CONDITION_ID: str = os.getenv("MARKET_CONDITION_ID", "")
    MARKET_QUESTION: str = os.getenv("MARKET_QUESTION", "Buffalo Bills to win Super Bowl 2026")

    # Strategy Parameters
    ENTRY_PROBABILITY: float = float(os.getenv("ENTRY_PROBABILITY", "0.80"))
    TAKE_PROFIT_PROBABILITY: float = float(os.getenv("TAKE_PROFIT_PROBABILITY", "0.85"))
    STOP_LOSS_PROBABILITY: float = float(os.getenv("STOP_LOSS_PROBABILITY", "0.78"))
    HEDGE_SELL_PERCENT: float = float(os.getenv("HEDGE_SELL_PERCENT", "1.0"))
    POLL_INTERVAL_SECONDS: int = int(os.getenv("POLL_INTERVAL_SECONDS", "20"))

    # Risk Management
    MAX_SLIPPAGE_PERCENT: float = float(os.getenv("MAX_SLIPPAGE_PERCENT", "2.0"))
    MIN_LIQUIDITY_USD: float = float(os.getenv("MIN_LIQUIDITY_USD", "5000"))

    # USDC Contract (Polygon Mainnet)
    USDC_ADDRESS: str = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"

    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        required_fields = [
            ("PRIVATE_KEY", cls.PRIVATE_KEY),
            ("POLYGON_RPC_URL", cls.POLYGON_RPC_URL),
        ]

        missing = [name for name, value in required_fields if not value]

        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")

        # Validate private key format
        if cls.PRIVATE_KEY and not cls.PRIVATE_KEY.startswith("0x"):
            cls.PRIVATE_KEY = f"0x{cls.PRIVATE_KEY}"

        return True

    @classmethod
    def display(cls) -> str:
        """Display configuration (hiding sensitive data)."""
        pk_preview = ""
        if cls.PRIVATE_KEY:
            pk_preview = f"{cls.PRIVATE_KEY[:6]}...{cls.PRIVATE_KEY[-4:]}"

        return f"""
╔══════════════════════════════════════════════════════════╗
║              POLYMARKET AGENT CONFIGURATION              ║
╚══════════════════════════════════════════════════════════╝

Network Configuration:
  • Chain: Polygon {'Mainnet' if cls.CHAIN_ID == 137 else 'Amoy Testnet'}
  • Chain ID: {cls.CHAIN_ID}
  • RPC: {cls.POLYGON_RPC_URL[:50]}...
  • Private Key: {pk_preview}

Market Configuration:
  • Condition ID: {cls.MARKET_CONDITION_ID[:10]}...{cls.MARKET_CONDITION_ID[-6:] if cls.MARKET_CONDITION_ID else 'NOT SET'}

Strategy Parameters:
  • Entry Probability: {cls.ENTRY_PROBABILITY * 100:.1f}%
  • Take Profit: {cls.TAKE_PROFIT_PROBABILITY * 100:.1f}%
  • Stop Loss: {cls.STOP_LOSS_PROBABILITY * 100:.1f}%
  • Hedge Sell %: {cls.HEDGE_SELL_PERCENT * 100:.0f}%
  • Poll Interval: {cls.POLL_INTERVAL_SECONDS}s

Risk Management:
  • Max Slippage: {cls.MAX_SLIPPAGE_PERCENT}%
  • Min Liquidity: ${cls.MIN_LIQUIDITY_USD:,.0f}
"""


# Create singleton instance
config = Config()
