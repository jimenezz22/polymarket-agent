#!/usr/bin/env python3
"""
Polymarket AI Hedge Agent - Main Loop

Automated trading agent that:
1. Monitors Polymarket probabilities in real-time
2. Takes profit when probability rises above threshold (default 85%)
3. Cuts losses when probability falls below threshold (default 78%)
4. Locks in gains through mathematical hedging
"""

import time
import sys
from datetime import datetime

from utils.config import config
from utils.logger import (
    console,
    log_info,
    log_success,
    log_warning,
    log_error,
    print_header
)
from utils.helpers import (
    GracefulKiller,
    retry_with_backoff,
    print_agent_status,
    calculate_sleep_until_next_poll,
    format_duration,
    validate_market_data
)

from wallet.wallet_manager import get_wallet
from api.polymarket_client import get_polymarket_client
from agent.position import get_position
from agent.strategy import create_strategy


def initialize_agent():
    """
    Initialize all agent components.

    Returns:
        Tuple of (wallet, client, position, strategy)
    """
    print_header("POLYMARKET AI HEDGE AGENT")

    log_info("Initializing agent components...")

    # Validate configuration
    try:
        config.validate()
        log_success("Configuration validated")
    except ValueError as e:
        log_error(f"Configuration error: {e}")
        sys.exit(1)

    # Initialize wallet
    try:
        wallet = get_wallet()
        if not wallet.is_connected():
            log_error("Failed to connect to Polygon RPC")
            sys.exit(1)

        log_success(f"Wallet connected: {wallet.get_address()[:10]}...{wallet.get_address()[-6:]}")

        # Check balance
        try:
            usdc_balance = wallet.get_usdc_balance()
            log_info(f"USDC Balance: ${usdc_balance:,.2f}")
        except Exception as e:
            log_warning(f"Could not fetch USDC balance: {e}")

    except Exception as e:
        log_error(f"Wallet initialization failed: {e}")
        sys.exit(1)

    # Initialize Polymarket client
    try:
        client = get_polymarket_client()
        log_success("Polymarket client initialized")
    except Exception as e:
        log_error(f"Polymarket client initialization failed: {e}")
        sys.exit(1)

    # Initialize position
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

    return wallet, client, position, strategy


def fetch_market_data(client):
    """
    Fetch current market data.

    Args:
        client: Polymarket client

    Returns:
        Tuple of (yes_price, no_price) or (None, None) on error
    """
    def _fetch():
        yes_price = client.get_yes_price(config.MARKET_CONDITION_ID)
        if yes_price is None:
            raise ValueError("Failed to fetch YES price")

        no_price = 1.0 - yes_price  # Binary market complement

        if not validate_market_data(yes_price, no_price):
            raise ValueError(f"Invalid market data: YES={yes_price}, NO={no_price}")

        return yes_price, no_price

    try:
        return retry_with_backoff(_fetch, max_retries=3)
    except Exception as e:
        log_error(f"Market data fetch failed: {e}")
        return None, None


def main_loop():
    """Main agent loop."""
    # Initialize
    wallet, client, position, strategy = initialize_agent()

    # Setup graceful shutdown
    killer = GracefulKiller()

    # Stats
    start_time = time.time()
    poll_count = 0
    last_action_time = None

    log_info("Starting monitoring loop...")
    log_info("Press Ctrl+C to stop gracefully")
    console.print()

    try:
        while not killer.kill_now:
            loop_start = time.time()
            poll_count += 1

            # Clear screen for clean display
            console.clear()
            print_header(f"POLYMARKET AGENT - Poll #{poll_count}")

            timestamp = datetime.utcnow().strftime("%H:%M:%S UTC")
            log_info(f"Timestamp: {timestamp}")
            log_info(f"Uptime: {format_duration(time.time() - start_time)}")

            if last_action_time:
                log_info(f"Last Action: {format_duration(time.time() - last_action_time)} ago")

            console.print()

            # Fetch market data
            log_info("Fetching market data...")
            yes_price, no_price = fetch_market_data(client)

            if yes_price is None:
                log_warning("Skipping this poll due to data fetch error")
                time.sleep(config.POLL_INTERVAL_SECONDS)
                continue

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

                # NOTE: In production, you would execute the trade here
                # For MVP/demo, we log the action instead
                log_warning("⚠ DEMO MODE: Trade execution disabled")
                log_info("To enable real trading:")
                log_info("  1. Uncomment strategy.execute_action(action) below")
                log_info("  2. Ensure you have API credentials configured")
                log_info("  3. Approve USDC spending on-chain first")

                # Uncomment to enable real trading:
                # try:
                #     result = strategy.execute_action(action)
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
            final_summary = position.get_position_summary(yes_price or 0, no_price or 0)
            log_info(f"Final Position: {final_summary['yes_shares']:.0f} YES, {final_summary['no_shares']:.0f} NO")
            log_info(f"Final Net PnL: ${final_summary['net_pnl']:,.2f}")

        log_success("Agent shutdown complete")


if __name__ == "__main__":
    main_loop()
