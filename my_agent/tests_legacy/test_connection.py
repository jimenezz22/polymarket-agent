#!/usr/bin/env python3
"""Test script for Phase 1 - Connection to Polymarket and Wallet."""

import time
from datetime import datetime
from utils.config import config
from utils.logger import (
    console,
    log_info,
    log_success,
    log_error,
    print_header,
    print_status_table,
    print_market_data
)
from wallet.wallet_manager import get_wallet
from api.polymarket_client import get_polymarket_client


def test_configuration():
    """Test that configuration is loaded properly."""
    print_header("Configuration Test")

    try:
        config.validate()
        log_success("Configuration loaded successfully")
        console.print(config.display())
        return True
    except ValueError as e:
        log_error(f"Configuration error: {e}")
        return False


def test_wallet_connection():
    """Test wallet connection to Polygon."""
    print_header("Wallet Connection Test")

    try:
        wallet = get_wallet()

        # Check RPC connection
        if not wallet.is_connected():
            log_error("Failed to connect to Polygon RPC")
            return False

        log_success(f"Connected to Polygon RPC: {config.POLYGON_RPC_URL[:50]}...")

        # Get network info
        network_info = wallet.get_network_info()
        print_status_table({
            "Chain ID": network_info["chain_id"],
            "Block Number": network_info["block_number"],
            "Gas Price": f"{network_info['gas_price']:.2f} gwei"
        })

        # Get wallet address
        address = wallet.get_address()
        log_success(f"Wallet address: {address}")

        # Get MATIC balance
        matic_balance = wallet.get_balance()
        log_info(f"MATIC balance: {matic_balance:.4f} MATIC")

        # Get USDC balance
        try:
            usdc_balance = wallet.get_usdc_balance()
            log_info(f"USDC balance: ${usdc_balance:,.2f}")
        except Exception as e:
            log_info(f"Could not fetch USDC balance (testnet may not have USDC): {str(e)[:50]}...")

        return True

    except Exception as e:
        log_error(f"Wallet connection failed: {e}")
        return False


def test_polymarket_connection():
    """Test connection to Polymarket API."""
    print_header("Polymarket API Test")

    try:
        client = get_polymarket_client()
        log_success("Polymarket client initialized")

        # Check if market condition ID is set
        if not config.MARKET_CONDITION_ID:
            log_warning("MARKET_CONDITION_ID not set in .env")
            log_info("Using default/demo mode")
            return True

        log_info(f"Market Condition ID: {config.MARKET_CONDITION_ID}")

        # Try to fetch market data
        market = client.get_market_by_condition_id(config.MARKET_CONDITION_ID)

        if market:
            log_success("Market found")
            print_status_table({
                "Question": market.get("question", "N/A"),
                "Condition ID": market.get("condition_id", "N/A")[:20] + "...",
            })
        else:
            log_warning("Market not found - might need valid condition ID")

        # Try to fetch YES price
        yes_price = client.get_yes_price(config.MARKET_CONDITION_ID)
        if yes_price:
            log_success(f"YES price: {yes_price:.4f} ({yes_price * 100:.2f}%)")
        else:
            log_warning("Could not fetch YES price")

        return True

    except Exception as e:
        log_error(f"Polymarket connection failed: {e}")
        return False


def monitor_market_prices(duration_seconds: int = 60, interval: int = 10):
    """
    Monitor market prices in real-time.

    Args:
        duration_seconds: How long to monitor (default 60s)
        interval: Polling interval in seconds (default 10s)
    """
    print_header("Live Market Monitoring")

    if not config.MARKET_CONDITION_ID:
        log_error("MARKET_CONDITION_ID not set in .env - cannot monitor")
        return

    client = get_polymarket_client()
    log_info(f"Monitoring for {duration_seconds}s (polling every {interval}s)")
    log_info("Press Ctrl+C to stop\n")

    start_time = time.time()

    try:
        while (time.time() - start_time) < duration_seconds:
            timestamp = datetime.now().strftime("%H:%M:%S")

            # Fetch current price
            yes_price = client.get_yes_price(config.MARKET_CONDITION_ID)

            if yes_price:
                # Fetch volume (optional)
                volume = client.get_market_volume_24h(config.MARKET_CONDITION_ID)
                print_market_data(timestamp, yes_price, volume)
            else:
                log_warning(f"[{timestamp}] Could not fetch price")

            time.sleep(interval)

    except KeyboardInterrupt:
        log_info("\nMonitoring stopped by user")


def main():
    """Run all connection tests."""
    console.clear()
    print_header("POLYMARKET AGENT - PHASE 1 CONNECTION TEST")
    console.print()

    # Run tests
    tests = [
        ("Configuration", test_configuration),
        ("Wallet", test_wallet_connection),
        ("Polymarket API", test_polymarket_connection),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            console.print()
        except Exception as e:
            log_error(f"{test_name} test crashed: {e}")
            results.append((test_name, False))
            console.print()

    # Summary
    print_header("Test Summary")
    for test_name, result in results:
        status = "[green]✓ PASS[/green]" if result else "[red]✗ FAIL[/red]"
        console.print(f"{status} - {test_name}")

    all_passed = all(result for _, result in results)

    console.print()

    if all_passed:
        log_success("All tests passed!")

        # Offer to run live monitoring
        console.print()
        response = console.input(
            "[cyan]Run live market monitoring for 60s? (y/n):[/cyan] "
        ).lower()

        if response == 'y':
            console.print()
            monitor_market_prices(duration_seconds=60, interval=10)
    else:
        log_error("Some tests failed - please check configuration")


if __name__ == "__main__":
    main()
