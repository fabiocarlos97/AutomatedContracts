from web3 import Web3
import json
import os
from eth_typing import Address
from utils import get_web3, load_abi
import logging
from decimal import Decimal
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Contract addresses
L2_MESSAGE_RECEIVER_ADDRESS = "0x2C0f43E5C92459F62C102517956A95E88E177e95"
WSTETH_ADDRESS = "0x6320cD32aA674d2898A68ec82e869385Fc5f7E2f"
MOR_ADDRESS = "0x454AE850eE61a98BF16FABA3a73fb0dD02D75C40"


def format_token_amount(amount: int, decimals: int = 18) -> str:
    """Format token amount with decimals for display"""
    return str(Decimal(amount) / Decimal(10**decimals))


def check_allowances(token_contract, owner_address, spender_address):
    """Check if token allowances are sufficient"""
    allowance = token_contract.functions.allowance(
        owner_address, spender_address
    ).call()
    balance = token_contract.functions.balanceOf(owner_address).call()
    return allowance >= balance


def main():
    w3 = get_web3("arbitrum_goerli")

    private_key = os.getenv("PRIVATE_KEY")
    if not private_key:
        raise ValueError("PRIVATE_KEY not found in environment variables")

    # Load contract ABIs
    l2_token_receiver_abi = load_abi("L2TokenReceiver.sol/L2TokenReceiver.json")
    erc20_abi = load_abi("ERC20.sol/ERC20.json")

    # Initialize contracts
    l2_token_receiver = w3.eth.contract(
        address=L2_MESSAGE_RECEIVER_ADDRESS, abi=l2_token_receiver_abi
    )
    wsteth = w3.eth.contract(address=WSTETH_ADDRESS, abi=erc20_abi)
    mor = w3.eth.contract(address=MOR_ADDRESS, abi=erc20_abi)

    # Get balances
    wsteth_balance = wsteth.functions.balanceOf(L2_MESSAGE_RECEIVER_ADDRESS).call()
    mor_balance = mor.functions.balanceOf(L2_MESSAGE_RECEIVER_ADDRESS).call()

    logger.info(f"Initial wstETH balance: {format_token_amount(wsteth_balance)} wstETH")
    logger.info(f"Initial MOR balance: {format_token_amount(mor_balance)} MOR")

    if wsteth_balance == 0 or mor_balance == 0:
        logger.warning("One or both token balances are 0. Aborting.")
        return

    # Check allowances
    account = w3.eth.account.from_key(private_key)

    # Build transaction
    try:
        nonce = w3.eth.get_transaction_count(account.address)

        # Estimate gas first
        gas_estimate = l2_token_receiver.functions.increaseLiquidityCurrentRange(
            86416, wsteth_balance, mor_balance, 0, 0
        ).estimate_gas({"from": account.address})

        gas_limit = int(gas_estimate * 1.2)  # Add 20% buffer

        tx = l2_token_receiver.functions.increaseLiquidityCurrentRange(
            86416, wsteth_balance, mor_balance, 0, 0
        ).build_transaction(
            {
                "from": account.address,
                "nonce": nonce,
                "gas": gas_limit,
                "gasPrice": w3.eth.gas_price,
            }
        )

        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        logger.info(f"Transaction sent. Hash: {tx_hash.hex()}")

        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if tx_receipt["status"] == 1:
            logger.info("Transaction successful!")
        else:
            logger.error("Transaction failed!")
            return

        # Get balances after
        wsteth_balance_after = wsteth.functions.balanceOf(
            L2_MESSAGE_RECEIVER_ADDRESS
        ).call()
        mor_balance_after = mor.functions.balanceOf(L2_MESSAGE_RECEIVER_ADDRESS).call()

        logger.info(
            f"Final wstETH balance: {format_token_amount(wsteth_balance_after)} wstETH"
        )
        logger.info(f"Final MOR balance: {format_token_amount(mor_balance_after)} MOR")

    except Exception as e:
        logger.error(f"Transaction failed: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        exit(1)
