from web3 import Web3
import json
import os
from eth_typing import Address
from utils import get_web3, load_abi

# Contract addresses
L2_MESSAGE_RECEIVER_ADDRESS = "0x2C0f43E5C92459F62C102517956A95E88E177e95"
WSTETH_ADDRESS = "0x6320cD32aA674d2898A68ec82e869385Fc5f7E2f"
MOR_ADDRESS = "0x454AE850eE61a98BF16FABA3a73fb0dD02D75C40"


def main():
    w3 = get_web3("arbitrum_goerli")

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

    print(f"wsteth balance of {L2_MESSAGE_RECEIVER_ADDRESS}: {wsteth_balance}")
    print(f"mor balance of {L2_MESSAGE_RECEIVER_ADDRESS}:    {mor_balance}")

    # Build transaction
    account = w3.eth.account.from_key("YOUR_PRIVATE_KEY_HERE")
    nonce = w3.eth.get_transaction_count(account.address)

    tx = l2_token_receiver.functions.increaseLiquidityCurrentRange(
        86416, wsteth_balance, mor_balance, 0, 0
    ).build_transaction(
        {
            "from": account.address,
            "nonce": nonce,
            "gas": 2000000,  # Adjust gas as needed
            "gasPrice": w3.eth.gas_price,
        }
    )

    # Sign and send transaction
    signed_tx = w3.eth.account.sign_transaction(tx, account.key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print("liquidity added")

    # Get balances after
    wsteth_balance_after = wsteth.functions.balanceOf(
        L2_MESSAGE_RECEIVER_ADDRESS
    ).call()
    mor_balance_after = mor.functions.balanceOf(L2_MESSAGE_RECEIVER_ADDRESS).call()

    print(f"wsteth balance of {L2_MESSAGE_RECEIVER_ADDRESS}: {wsteth_balance_after}")
    print(f"mor balance of {L2_MESSAGE_RECEIVER_ADDRESS}:    {mor_balance_after}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
