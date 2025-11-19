"""Polymarket API client using py-clob-client."""

from typing import Optional, Dict, Tuple, List
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, MarketOrderArgs
from utils.config import config
from utils.logger import log_warning, log_error


class PolymarketClient:
    """Wrapper for Polymarket CLOB client."""

    def __init__(self, host: str = "https://clob.polymarket.com"):
        """
        Initialize Polymarket client.

        Args:
            host: CLOB API host URL
        """
        self.host = host
        self.client = ClobClient(
            host=host,
            chain_id=config.CHAIN_ID,
        )

    def get_market_by_condition_id(self, condition_id: str) -> Optional[Dict]:
        """
        Get market information by condition ID.

        Args:
            condition_id: Market condition ID (0x...)

        Returns:
            Market data dictionary or None if not found
        """
        try:
            # For now, return a placeholder since we don't have API credentials
            # In production, this would use authenticated client methods
            log_warning("Market data fetch requires Polymarket API credentials")
            return {
                "condition_id": condition_id,
                "question": "Demo Market (requires API auth)",
                "active": True
            }
        except Exception as e:
            log_error(f"Error fetching market: {e}")
            return None

    def get_yes_price(self, condition_id: str) -> Optional[float]:
        """
        Get current YES token price (= implied probability).

        Args:
            condition_id: Market condition ID

        Returns:
            YES price as float (0.0-1.0) or None if error
        """
        try:
            # For demo purposes, return simulated price
            # In production, this would fetch real market data
            log_warning("Price fetch requires Polymarket API credentials - using demo data")
            return 0.82  # Demo price: 82%
        except Exception as e:
            log_error(f"Error fetching YES price: {e}")
            return None

    def get_user_shares(self, address: str, condition_id: str) -> Tuple[float, float]:
        """
        Get user's current share holdings.

        Args:
            address: User wallet address
            condition_id: Market condition ID

        Returns:
            Tuple of (yes_shares, no_shares)
        """
        try:
            # Get user's positions
            positions = self.client.get_positions(address)

            yes_shares = 0.0
            no_shares = 0.0

            for position in positions:
                if position.get("condition_id") == condition_id:
                    outcome_index = position.get("outcome_index", 0)
                    size = float(position.get("size", 0))

                    if outcome_index == 0:  # YES
                        yes_shares = size
                    elif outcome_index == 1:  # NO
                        no_shares = size

            return (yes_shares, no_shares)
        except Exception as e:
            print(f"Error fetching user shares: {e}")
            return (0.0, 0.0)

    def get_order_book(self, condition_id: str) -> Optional[Dict]:
        """
        Get full order book for a market.

        Args:
            condition_id: Market condition ID

        Returns:
            Order book with bids and asks
        """
        try:
            book = self.client.get_order_book(condition_id)
            return book
        except Exception as e:
            print(f"Error fetching order book: {e}")
            return None

    def get_market_prices(self, condition_id: str) -> Optional[Dict[str, float]]:
        """
        Get current market prices for YES and NO.

        Args:
            condition_id: Market condition ID

        Returns:
            Dictionary with yes_price, no_price, or None
        """
        try:
            book = self.get_order_book(condition_id)

            if not book:
                return None

            result = {}

            # Get YES price (best ask for outcome 0)
            if "asks" in book and book["asks"]:
                result["yes_price"] = float(book["asks"][0].get("price", 0))

            # Get NO price (best ask for outcome 1)
            # In a binary market: NO price ≈ 1 - YES price
            if "yes_price" in result:
                result["no_price"] = 1.0 - result["yes_price"]

            return result if result else None
        except Exception as e:
            print(f"Error fetching market prices: {e}")
            return None

    def place_order(
        self,
        condition_id: str,
        outcome_index: int,
        amount_shares: float,
        price: Optional[float] = None,
        side: str = "BUY"
    ) -> Optional[str]:
        """
        Place an order on Polymarket.

        Args:
            condition_id: Market condition ID
            outcome_index: 0 for YES, 1 for NO
            amount_shares: Number of shares
            price: Limit price (0.0-1.0). If None, places market order.
            side: "BUY" or "SELL"

        Returns:
            Order ID if successful, None otherwise
        """
        try:
            # Market order (fill-or-kill with slippage tolerance)
            if price is None:
                # Get current market price
                current_price = self.get_yes_price(condition_id)
                if not current_price:
                    print("Could not determine market price")
                    return None

                # Apply slippage tolerance
                slippage = config.MAX_SLIPPAGE_PERCENT / 100.0

                if side == "BUY":
                    # Willing to pay up to X% more
                    price = current_price * (1 + slippage)
                else:  # SELL
                    # Willing to accept up to X% less
                    price = current_price * (1 - slippage)

                # Clamp to valid range
                price = max(0.01, min(0.99, price))

            # TODO: Implement actual order placement using py-clob-client
            # This requires authentication with API keys
            # For now, return a placeholder

            print(f"[PLACEHOLDER] Order: {side} {amount_shares} shares "
                  f"@ ${price:.4f} (outcome {outcome_index})")

            return "placeholder_order_id"

        except Exception as e:
            print(f"Error placing order: {e}")
            return None

    def get_market_volume_24h(self, condition_id: str) -> Optional[float]:
        """
        Get 24h trading volume for a market.

        Args:
            condition_id: Market condition ID

        Returns:
            Volume in USD or None
        """
        try:
            market = self.get_market_by_condition_id(condition_id)
            if market:
                volume = market.get("volume_24h") or market.get("volume")
                if volume:
                    return float(volume)
            return None
        except Exception as e:
            print(f"Error fetching volume: {e}")
            return None


# Singleton instance
_client_instance: Optional[PolymarketClient] = None


def get_polymarket_client() -> PolymarketClient:
    """Get or create Polymarket client singleton."""
    global _client_instance
    if _client_instance is None:
        _client_instance = PolymarketClient()
    return _client_instance
