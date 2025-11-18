"""Web3 wallet management for Polygon network."""

from typing import Optional
from web3 import Web3
try:
    from web3.middleware import ExtraDataToPOAMiddleware
    geth_poa_middleware = ExtraDataToPOAMiddleware
except ImportError:
    from web3.middleware import geth_poa_middleware
from eth_account import Account
from utils.config import config


class WalletManager:
    """Manages Web3 wallet operations on Polygon."""

    def __init__(self, private_key: Optional[str] = None, rpc_url: Optional[str] = None):
        """
        Initialize wallet manager.

        Args:
            private_key: Private key (with or without 0x prefix). If None, loads from config.
            rpc_url: RPC URL for Polygon. If None, loads from config.
        """
        self.rpc_url = rpc_url or config.POLYGON_RPC_URL
        self.private_key = private_key or config.PRIVATE_KEY

        # Ensure private key has 0x prefix
        if self.private_key and not self.private_key.startswith("0x"):
            self.private_key = f"0x{self.private_key}"

        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))

        # Add PoA middleware for Polygon
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        # Create account from private key
        if self.private_key:
            self.account = Account.from_key(self.private_key)
            self.address = self.account.address
        else:
            self.account = None
            self.address = None

    def is_connected(self) -> bool:
        """Check if connected to Polygon RPC."""
        try:
            return self.w3.is_connected()
        except Exception:
            return False

    def get_address(self) -> str:
        """Get wallet address."""
        if not self.address:
            raise ValueError("Wallet not initialized with private key")
        return self.address

    def get_balance(self) -> float:
        """
        Get native MATIC balance.

        Returns:
            Balance in MATIC
        """
        if not self.address:
            raise ValueError("Wallet not initialized")

        balance_wei = self.w3.eth.get_balance(self.address)
        balance_matic = self.w3.from_wei(balance_wei, "ether")
        return float(balance_matic)

    def get_usdc_balance(self) -> float:
        """
        Get USDC balance.

        Returns:
            Balance in USDC (6 decimals)
        """
        if not self.address:
            raise ValueError("Wallet not initialized")

        # USDC contract ABI (minimal - just balanceOf)
        usdc_abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function",
            }
        ]

        usdc_contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(config.USDC_ADDRESS),
            abi=usdc_abi
        )

        balance_raw = usdc_contract.functions.balanceOf(self.address).call()
        # USDC has 6 decimals
        balance_usdc = balance_raw / 10**6
        return float(balance_usdc)

    def approve_token(
        self,
        token_address: str,
        spender_address: str,
        amount: Optional[int] = None
    ) -> str:
        """
        Approve a contract to spend tokens.

        Args:
            token_address: ERC20 token contract address
            spender_address: Address to approve
            amount: Amount to approve (in wei). If None, approves max uint256.

        Returns:
            Transaction hash
        """
        if not self.account:
            raise ValueError("Wallet not initialized")

        # Max approval if amount not specified
        if amount is None:
            amount = 2**256 - 1

        # ERC20 approve ABI
        erc20_abi = [
            {
                "constant": False,
                "inputs": [
                    {"name": "_spender", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "approve",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function",
            }
        ]

        token_contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=erc20_abi
        )

        # Build transaction
        tx = token_contract.functions.approve(
            Web3.to_checksum_address(spender_address),
            amount
        ).build_transaction({
            'from': self.address,
            'nonce': self.w3.eth.get_transaction_count(self.address),
            'gas': 100000,
            'gasPrice': self.w3.eth.gas_price,
        })

        # Sign and send
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return self.w3.to_hex(tx_hash)

    def sign_transaction(self, transaction: dict) -> str:
        """
        Sign and send a transaction.

        Args:
            transaction: Transaction dictionary

        Returns:
            Transaction hash
        """
        if not self.account:
            raise ValueError("Wallet not initialized")

        # Add nonce if not present
        if 'nonce' not in transaction:
            transaction['nonce'] = self.w3.eth.get_transaction_count(self.address)

        # Add gas price if not present
        if 'gasPrice' not in transaction:
            transaction['gasPrice'] = self.w3.eth.gas_price

        # Sign transaction
        signed_tx = self.w3.eth.account.sign_transaction(transaction, self.private_key)

        # Send transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return self.w3.to_hex(tx_hash)

    def wait_for_transaction(self, tx_hash: str, timeout: int = 120) -> dict:
        """
        Wait for transaction to be mined.

        Args:
            tx_hash: Transaction hash
            timeout: Timeout in seconds

        Returns:
            Transaction receipt
        """
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
        return dict(receipt)

    def get_network_info(self) -> dict:
        """Get current network information."""
        return {
            "connected": self.is_connected(),
            "chain_id": self.w3.eth.chain_id if self.is_connected() else None,
            "block_number": self.w3.eth.block_number if self.is_connected() else None,
            "gas_price": float(self.w3.from_wei(self.w3.eth.gas_price, "gwei")) if self.is_connected() else None,
        }


# Singleton instance
_wallet_instance: Optional[WalletManager] = None


def get_wallet() -> WalletManager:
    """Get or create wallet manager singleton."""
    global _wallet_instance
    if _wallet_instance is None:
        _wallet_instance = WalletManager()
    return _wallet_instance
