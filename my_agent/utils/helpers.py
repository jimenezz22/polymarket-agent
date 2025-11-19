"""Helper utilities for the agent."""

import time
import signal
import sys
from typing import Callable, Optional
from datetime import datetime
from rich.table import Table
from my_agent.utils.logger import console


class GracefulKiller:
    """Handle graceful shutdown on SIGINT/SIGTERM."""

    def __init__(self):
        self.kill_now = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        """Set kill flag on signal."""
        self.kill_now = True


def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Optional[any]:
    """
    Retry a function with exponential backoff.

    Args:
        func: Function to retry
        max_retries: Maximum retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for each retry
        exceptions: Tuple of exceptions to catch

    Returns:
        Function result or None if all retries failed
    """
    delay = initial_delay

    for attempt in range(max_retries):
        try:
            return func()
        except exceptions as e:
            if attempt == max_retries - 1:
                raise e

            time.sleep(delay)
            delay *= backoff_factor

    return None


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format timestamp for display.

    Args:
        dt: Datetime object (default: now)

    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.utcnow()

    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def create_status_table(data: dict, title: str = "Status") -> Table:
    """
    Create a Rich table for status display.

    Args:
        data: Dictionary of key-value pairs
        title: Table title

    Returns:
        Rich Table object
    """
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")

    for key, value in data.items():
        table.add_row(key, str(value))

    return table


def print_agent_status(
    current_prob: float,
    yes_price: float,
    no_price: float,
    position_summary: dict,
    action: dict
):
    """
    Print comprehensive agent status.

    Args:
        current_prob: Current probability
        yes_price: YES price
        no_price: NO price
        position_summary: Position summary dict
        action: Recommended action dict
    """
    # Market data
    market_table = Table(title="📊 Market Data", show_header=False, box=None)
    market_table.add_column(style="cyan")
    market_table.add_column(style="white")

    prob_color = "green" if current_prob >= 0.85 else "red" if current_prob <= 0.78 else "yellow"

    market_table.add_row("Current Probability", f"[{prob_color}]{current_prob * 100:.2f}%[/{prob_color}]")
    market_table.add_row("YES Price", f"${yes_price:.4f}")
    market_table.add_row("NO Price", f"${no_price:.4f}")

    console.print(market_table)
    console.print()

    # Position
    if position_summary["yes_shares"] > 0 or position_summary["no_shares"] > 0:
        position_table = Table(title="💼 Position", show_header=False, box=None)
        position_table.add_column(style="cyan")
        position_table.add_column(style="white")

        position_table.add_row("YES Shares", f"{position_summary['yes_shares']:.0f}")
        position_table.add_row("NO Shares", f"{position_summary['no_shares']:.0f}")
        position_table.add_row("Total Invested", f"${position_summary['total_invested']:,.2f}")
        position_table.add_row("Total Withdrawn", f"${position_summary['total_withdrawn']:,.2f}")

        pnl_color = "green" if position_summary['net_pnl'] >= 0 else "red"
        position_table.add_row(
            "Net PnL",
            f"[{pnl_color}]${position_summary['net_pnl']:,.2f} ({position_summary['roi']:.2f}%)[/{pnl_color}]"
        )

        if position_summary.get('locked_pnl', 0) > 0:
            position_table.add_row("Locked PnL", f"[green]${position_summary['locked_pnl']:,.2f}[/green]")

        console.print(position_table)
        console.print()

    # Action
    action_table = Table(title="🎯 Recommended Action", show_header=False, box=None)
    action_table.add_column(style="cyan")
    action_table.add_column(style="white")

    action_type = action["action"]
    action_color = "green" if action_type == "TAKE_PROFIT" else "red" if action_type == "STOP_LOSS" else "yellow"

    action_table.add_row("Action", f"[{action_color}]{action_type}[/{action_color}]")
    action_table.add_row("Reason", action["reason"])

    console.print(action_table)


def calculate_sleep_until_next_poll(
    poll_interval: int,
    last_poll_time: float
) -> float:
    """
    Calculate seconds to sleep until next poll.

    Args:
        poll_interval: Desired poll interval in seconds
        last_poll_time: Time of last poll (from time.time())

    Returns:
        Seconds to sleep (minimum 0)
    """
    elapsed = time.time() - last_poll_time
    sleep_time = max(0, poll_interval - elapsed)
    return sleep_time


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "2h 15m 30s")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)


def validate_market_data(yes_price: float, no_price: float) -> bool:
    """
    Validate market data is reasonable.

    Args:
        yes_price: YES price
        no_price: NO price

    Returns:
        True if valid, False otherwise
    """
    # Prices should be between 0 and 1
    if not (0 <= yes_price <= 1 and 0 <= no_price <= 1):
        return False

    # For binary markets, YES + NO should be close to 1.0
    total = yes_price + no_price
    if not (0.95 <= total <= 1.05):
        return False

    return True


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers.

    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero

    Returns:
        Result or default
    """
    if denominator == 0:
        return default
    return numerator / denominator
