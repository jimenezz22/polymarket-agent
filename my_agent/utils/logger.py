"""Logging utilities using Rich library."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from datetime import datetime

# Global console instance
console = Console()


def log_info(message: str):
    """Log info message."""
    console.print(f"[blue]ℹ[/blue] {message}")


def log_success(message: str):
    """Log success message."""
    console.print(f"[green]✓[/green] {message}")


def log_warning(message: str):
    """Log warning message."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def log_error(message: str):
    """Log error message."""
    console.print(f"[red]✗[/red] {message}")


def log_trade(action: str, details: str):
    """Log trade action."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    console.print(f"[cyan][{timestamp}][/cyan] [bold]{action}[/bold]: {details}")


def print_header(title: str):
    """Print a formatted header."""
    console.print(Panel.fit(f"[bold cyan]{title}[/bold cyan]"))


def print_status_table(data: dict):
    """Print a status table with key-value pairs."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="cyan", no_wrap=True)
    table.add_column(style="white")

    for key, value in data.items():
        table.add_row(f"{key}:", str(value))

    console.print(table)


def print_market_data(timestamp: str, yes_price: float, volume: float = None):
    """Print formatted market data."""
    prob_pct = yes_price * 100
    color = "green" if yes_price >= 0.85 else "red" if yes_price <= 0.78 else "yellow"

    parts = [
        f"[dim]{timestamp}[/dim]",
        f"YES: [bold {color}]{yes_price:.4f}[/bold {color}] ({prob_pct:.2f}%)"
    ]

    if volume:
        parts.append(f"Volume: [cyan]${volume:,.0f}[/cyan]")

    console.print(" | ".join(parts))
