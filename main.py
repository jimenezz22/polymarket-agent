#!/usr/bin/env python3
"""
Polymarket AI Hedge Agent - Main Entry Point

Integrates official Polymarket Agents framework with custom hedging strategy.
Built on top of: https://github.com/Polymarket/agents
"""

import time
import sys
import warnings
from datetime import datetime
from typing import Optional

# Suppress debug output from agents framework
import os
os.environ['PYTHONWARNINGS'] = 'ignore'
warnings.filterwarnings('ignore')

# Polymarket Agents Framework
from agents.polymarket.polymarket import Polymarket
from agents.polymarket.gamma import GammaMarketClient

# Our Custom Hedging Strategy
from my_agent.strategy import TradingStrategy, create_strategy
from my_agent.position import Position, get_position
from my_agent.utils.config import config
from my_agent.utils.logger import (
    console,
    log_info,
    log_success,
    log_warning,
    log_error,
    print_header
)
from my_agent.utils.helpers import (
    GracefulKiller,
    retry_with_backoff,
    print_agent_status,
    calculate_sleep_until_next_poll,
    format_duration,
    validate_market_data
)


def initialize_agent():
    """
    Initialize all agent components using Polymarket Agents framework.

    Returns:
        Tuple of (polymarket_client, gamma_client, position, strategy)
    """
    print_header("POLYMARKET AI HEDGE AGENT")
    log_info("Built on Polymarket Agents framework")

    # Validate configuration
    try:
        config.validate()
        log_success("Configuration validated")
    except ValueError as e:
        log_error(f"Configuration error: {e}")
        sys.exit(1)

    # Initialize Polymarket client (from agents framework)
    try:
        polymarket_client = Polymarket()
        log_success("Polymarket client initialized (agents framework)")

        # Get wallet address
        wallet_address = polymarket_client.get_address_for_private_key()
        log_info(f"Wallet: {wallet_address[:10]}...{wallet_address[-6:]}")

        # Check USDC balance
        try:
            balance = polymarket_client.get_balance_usdc()
            log_info(f"USDC Balance: ${balance:,.2f}")
        except Exception as e:
            log_warning(f"Could not fetch USDC balance: {e}")

    except Exception as e:
        log_error(f"Polymarket client initialization failed: {e}")
        sys.exit(1)

    # Initialize Gamma client for market data
    try:
        gamma_client = GammaMarketClient()
        log_success("Gamma market client initialized")
    except Exception as e:
        log_error(f"Gamma client initialization failed: {e}")
        sys.exit(1)

    # Initialize position manager
    try:
        position = get_position()

        if position.has_position():
            log_info(f"Loaded existing position: {position.yes_shares:.0f} YES, {position.no_shares:.0f} NO")
        else:
            log_info("No existing position found")

    except Exception as e:
        log_error(f"Position initialization failed: {e}")
        sys.exit(1)

    # Initialize strategy
    try:
        strategy = create_strategy(position)
        log_success("Trading strategy initialized")
        log_info(f"  Take Profit: ≥{config.TAKE_PROFIT_PROBABILITY * 100:.1f}%")
        log_info(f"  Stop Loss: ≤{config.STOP_LOSS_PROBABILITY * 100:.1f}%")
        log_info(f"  Hedge Sell %: {config.HEDGE_SELL_PERCENT * 100:.0f}%")
        log_info(f"  Poll Interval: {config.POLL_INTERVAL_SECONDS}s")

    except Exception as e:
        log_error(f"Strategy initialization failed: {e}")
        sys.exit(1)

    console.print()
    log_success("All components initialized successfully!")
    console.print()

    return polymarket_client, gamma_client, position, strategy


def fetch_market_data(gamma_client: GammaMarketClient, condition_id: str) -> Optional[tuple]:
    """
    Fetch current market data from Gamma API.

    Args:
        gamma_client: Gamma market client
        condition_id: Market condition ID

    Returns:
        Tuple of (yes_price, no_price) or None on error
    """
    def _fetch():
        import json
        # Fetch raw data without pydantic parsing to avoid debug logs
        # parse_pydantic=False prevents framework from logging every market
        # NOTE: Gamma API uses 'condition_ids' (plural), not 'condition_id'
        markets = gamma_client.get_markets(
            {"condition_ids": condition_id.lower()},  # Plural & lowercase
            parse_pydantic=False  # Avoid debug output
        )

        if not markets or len(markets) == 0:
            raise ValueError(f"No market found for condition_id: {condition_id}")

        market = markets[0]

        # Parse prices manually
        prices = market.get('outcomePrices')
        if not prices:
            raise ValueError("Market does not have outcome prices")

        # Prices might be stringified JSON
        if isinstance(prices, str):
            prices = json.loads(prices)

        if len(prices) < 2:
            raise ValueError("Invalid outcome prices format")

        yes_price = float(prices[0])
        no_price = float(prices[1])

        if not validate_market_data(yes_price, no_price):
            raise ValueError(f"Invalid market data: YES={yes_price}, NO={no_price}")

        return yes_price, no_price

    try:
        return retry_with_backoff(_fetch, max_retries=3)
    except Exception as e:
        log_error(f"Market data fetch failed: {e}")
        return None


def main_loop():
    """Main agent loop."""
    # Initialize
    polymarket_client, gamma_client, position, strategy = initialize_agent()

    # Setup graceful shutdown
    killer = GracefulKiller()

    # Stats
    start_time = time.time()
    poll_count = 0
    last_action_time = None

    log_info("Starting monitoring loop...")
    log_info("Press Ctrl+C to stop gracefully")
    console.print()

    # Market condition ID
    condition_id = config.MARKET_CONDITION_ID
    if not condition_id:
        log_error("MARKET_CONDITION_ID not set in .env")
        sys.exit(1)

    try:
        while not killer.kill_now:
            loop_start = time.time()
            poll_count += 1

            # Clear screen for clean display
            console.clear()
            print_header(f"POLYMARKET HEDGE AGENT - Poll #{poll_count}")

            timestamp = datetime.utcnow().strftime("%H:%M:%S UTC")
            log_info(f"Timestamp: {timestamp}")
            log_info(f"Uptime: {format_duration(time.time() - start_time)}")

            if last_action_time:
                log_info(f"Last Action: {format_duration(time.time() - last_action_time)} ago")

            console.print()

            # Fetch market data from Gamma API
            log_info(f"Fetching market data for condition: {condition_id[:10]}...")
            result = fetch_market_data(gamma_client, condition_id)

            if result is None:
                log_warning("Skipping this poll due to data fetch error")
                time.sleep(config.POLL_INTERVAL_SECONDS)
                continue

            yes_price, no_price = result
            current_prob = yes_price

            # Get position summary
            position_summary = position.get_position_summary(yes_price, no_price)

            # Evaluate strategy
            action = strategy.evaluate(
                current_prob=current_prob,
                yes_price=yes_price,
                no_price=no_price
            )

            console.print()

            # Display status
            print_agent_status(
                current_prob=current_prob,
                yes_price=yes_price,
                no_price=no_price,
                position_summary=position_summary,
                action=action
            )

            console.print()

            # Execute action if needed
            if action["action"] in ["TAKE_PROFIT", "STOP_LOSS"]:
                log_warning(f"⚠ ACTION REQUIRED: {action['action']}")
                log_info(f"Reason: {action['reason']}")

                # NOTE: In production, integrate with polymarket_client for real trades
                log_warning("⚠ DEMO MODE: Trade execution disabled")
                log_info("To enable real trading:")
                log_info("  1. Ensure USDC approvals are set (run agents approval script)")
                log_info("  2. Integrate strategy with polymarket_client.place_order()")
                log_info("  3. Test on testnet first!")

                # TODO: Real implementation
                # try:
                #     if action["action"] == "TAKE_PROFIT":
                #         # Sell YES shares via polymarket_client
                #         # Buy NO shares with proceeds
                #         result = strategy.execute_action(action)
                #     elif action["action"] == "STOP_LOSS":
                #         # Sell all shares
                #         result = strategy.execute_action(action)
                #
                #     if result:
                #         log_success(f"Action executed: {result}")
                #         last_action_time = time.time()
                # except Exception as e:
                #     log_error(f"Action execution failed: {e}")

            elif action["action"] == "HOLD":
                log_info("💼 HOLD - Position maintained")

            elif action["action"] == "WAIT":
                log_info("⏸ WAIT - No position open")

            console.print()

            # Calculate sleep time
            sleep_time = calculate_sleep_until_next_poll(
                config.POLL_INTERVAL_SECONDS,
                loop_start
            )

            if sleep_time > 0:
                log_info(f"Next poll in {sleep_time:.0f}s...")
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        log_info("\n⚠ Received interrupt signal")

    except Exception as e:
        log_error(f"Unexpected error in main loop: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        console.print()
        print_header("SHUTDOWN")

        log_info("Saving final state...")
        position.save()

        # Display final stats
        runtime = time.time() - start_time
        log_info(f"Total Runtime: {format_duration(runtime)}")
        log_info(f"Total Polls: {poll_count}")

        if position.has_position():
            # Use last known prices or 0
            final_yes_price = result[0] if result else 0
            final_no_price = result[1] if result else 0
            final_summary = position.get_position_summary(final_yes_price, final_no_price)
            log_info(f"Final Position: {final_summary['yes_shares']:.0f} YES, {final_summary['no_shares']:.0f} NO")
            log_info(f"Final Net PnL: ${final_summary['net_pnl']:,.2f}")

        log_success("Agent shutdown complete")


if __name__ == "__main__":
    main_loop()
