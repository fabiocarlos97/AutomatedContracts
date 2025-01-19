from web3 import Web3
from eth_account import Account
from web3.middleware import geth_poa_middleware
import json
import os
from pathlib import Path


def wei(amount):
    return Web3.toWei(amount, "ether")


def load_abi(contract_name):
    # Look for ABI in standard artifacts directory
    artifacts_dir = Path(__file__).parent.parent / "artifacts" / "contracts"
    abi_file = artifacts_dir / f"{contract_name}.sol" / f"{contract_name}.json"

    if not abi_file.exists():
        raise FileNotFoundError(f"ABI file not found at {abi_file}")

    with open(abi_file) as f:
        contract_json = json.load(f)
        return contract_json["abi"]


async def wait_for_transaction(w3, tx_hash, timeout=120):
    """Wait for transaction to be mined and return receipt."""
    try:
        return w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
    except Exception as e:
        raise Exception(f"Transaction failed: {e}")


async def main():
    # Connect to network
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    if not w3.is_connected():
        raise Exception("Failed to connect to Ethereum node")

    # Load accounts
    owner_private_key = os.getenv(
        "OWNER_PRIVATE_KEY",
        "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
    )
    signer_private_key = os.getenv(
        "SIGNER_PRIVATE_KEY",
        "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",
    )

    owner = w3.eth.account.from_key(owner_private_key)
    signer = w3.eth.account.from_key(signer_private_key)

    print(f"Owner address: {owner.address}")
    print(f"Signer address: {signer.address}")

    # Send ETH to signer if needed
    balance = w3.eth.get_balance(signer.address)
    if balance < wei(0.2):  # Ensure signer has enough ETH
        tx = {
            "to": signer.address,
            "value": wei(0.1),
            "gas": 21000,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(owner.address),
        }
        signed_tx = owner.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = await wait_for_transaction(w3, tx_hash)
        print(
            f"Funded signer with 0.1 ETH. Transaction: {receipt['transactionHash'].hex()}"
        )

    # Load distribution contract
    distribution_address = "0x47176B2Af9885dC6C4575d4eFd63895f7Aaa4790"
    try:
        distribution_abi = load_abi("Distribution")
        distribution = w3.eth.contract(
            address=distribution_address, abi=distribution_abi
        )
    except FileNotFoundError:
        # Fallback to minimal ABI if full ABI not found
        distribution = w3.eth.contract(
            address=distribution_address,
            abi=[
                {
                    "inputs": [
                        {"type": "uint256", "name": "tokenId"},
                        {"type": "address", "name": "recipient"},
                    ],
                    "name": "claim",
                    "outputs": [],
                    "stateMutability": "payable",
                    "type": "function",
                }
            ],
        )

    # Execute claim transaction
    try:
        tx = distribution.functions.claim(4, signer.address).build_transaction(
            {
                "value": wei(0.01),
                "from": signer.address,
                "nonce": w3.eth.get_transaction_count(signer.address),
                "gas": 200000,
                "gasPrice": w3.eth.gas_price,
            }
        )
        signed_tx = signer.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = await wait_for_transaction(w3, tx_hash)

        if receipt["status"] == 1:
            print(
                f"Claim executed successfully. Transaction: {receipt['transactionHash'].hex()}"
            )
        else:
            raise Exception("Claim transaction reverted")

    except Exception as e:
        raise Exception(f"Failed to execute claim: {e}")


if __name__ == "__main__":
    try:
        import asyncio

        asyncio.run(main())
    except Exception as error:
        print(f"Error: {error}")
