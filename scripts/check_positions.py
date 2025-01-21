from web3 import Web3
from eth_account import Account
from web3.middleware import geth_poa_middleware
import json
import os
from pathlib import Path
from typing import List, Dict, Any
from decimal import Decimal


def load_abi(contract_name: str) -> List[Dict[str, Any]]:
    """Load ABI from artifacts directory."""
    artifacts_dir = Path(__file__).parent.parent / "artifacts" / "contracts"
    abi_file = artifacts_dir / f"{contract_name}.sol" / f"{contract_name}.json"

    if not abi_file.exists():
        raise FileNotFoundError(f"ABI file not found at {abi_file}")

    with open(abi_file) as f:
        contract_json = json.load(f)
        return contract_json["abi"]


def format_token_amount(amount: int, decimals: int) -> str:
    """Format token amount with proper decimals."""
    return str(Decimal(amount) / Decimal(10**decimals))


async def get_position_info(position_contract, position_id: int) -> Dict[str, Any]:
    """Get detailed information about a specific position."""
    try:
        position = await position_contract.functions.positions(position_id).call()
        return {
            "id": position_id,
            "owner": position[0],
            "collateralAmount": position[1],
            "debtAmount": position[2],
            "lastInteractionTime": position[3],
        }
    except Exception as e:
        print(f"Error fetching position {position_id}: {e}")
        return None


async def main():
    # Connect to network
    w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL", "http://127.0.0.1:8545")))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    if not w3.is_connected():
        raise Exception("Failed to connect to Ethereum node")

    # Load contract
    vault_address = os.getenv(
        "VAULT_ADDRESS", "0x47176B2Af9885dC6C4575d4eFd63895f7Aaa4790"
    )
    try:
        vault_abi = load_abi("Vault")
        vault = w3.eth.contract(address=vault_address, abi=vault_abi)
    except FileNotFoundError:
        print("Warning: Full ABI not found, using minimal ABI")
        # Minimal ABI for position checking
        vault = w3.eth.contract(
            address=vault_address,
            abi=[
                {
                    "inputs": [{"type": "uint256"}],
                    "name": "positions",
                    "outputs": [
                        {"type": "address", "name": "owner"},
                        {"type": "uint256", "name": "collateralAmount"},
                        {"type": "uint256", "name": "debtAmount"},
                        {"type": "uint256", "name": "lastInteractionTime"},
                    ],
                    "stateMutability": "view",
                    "type": "function",
                },
                {
                    "inputs": [],
                    "name": "totalPositions",
                    "outputs": [{"type": "uint256"}],
                    "stateMutability": "view",
                    "type": "function",
                },
            ],
        )

    try:
        # Get total number of positions
        total_positions = await vault.functions.totalPositions().call()
        print(f"Total positions: {total_positions}")

        # Fetch all active positions
        active_positions = []
        for position_id in range(1, total_positions + 1):
            position = await get_position_info(vault, position_id)
            if position and position["collateralAmount"] > 0:
                active_positions.append(position)

        # Display position information
        print("\nActive Positions:")
        print("-" * 80)
        for position in active_positions:
            print(f"Position ID: {position['id']}")
            print(f"Owner: {position['owner']}")
            print(
                f"Collateral: {format_token_amount(position['collateralAmount'], 18)} ETH"
            )
            print(f"Debt: {format_token_amount(position['debtAmount'], 18)} tokens")
            print(f"Last Interaction: {position['lastInteractionTime']}")
            print("-" * 80)

        # Calculate some statistics
        total_collateral = sum(p["collateralAmount"] for p in active_positions)
        total_debt = sum(p["debtAmount"] for p in active_positions)

        print("\nSummary:")
        print(f"Total Active Positions: {len(active_positions)}")
        print(f"Total Collateral: {format_token_amount(total_collateral, 18)} ETH")
        print(f"Total Debt: {format_token_amount(total_debt, 18)} tokens")

    except Exception as e:
        raise Exception(f"Failed to check positions: {e}")


if __name__ == "__main__":
    try:
        import asyncio

        asyncio.run(main())
    except Exception as error:
        print(f"Error: {error}")
