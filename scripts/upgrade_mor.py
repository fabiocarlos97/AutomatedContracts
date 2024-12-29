from web3 import Web3
import json
import os

# Connect to local network
w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))

# Contract addresses
WETH = "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1"
IMPERSONATED_ADDRESS = "0x151c2b49CdEC10B150B2763dF3d1C00D70C90956"
L2_MESSAGE_RECEIVER_ADDRESS = "0xd4a8ECcBe696295e68572A98b1aA70Aa9277d427"


def load_abi(filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, f"../artifacts/contracts/{filename}")) as f:
        return json.load(f)["abi"]


async def main():
    # Load contract ABI
    l2_message_receiver_abi = load_abi("L2MessageReceiver.sol/L2MessageReceiver.json")

    # Impersonate account (this requires unlocking the account in your local node)
    w3.provider.make_request("hardhat_impersonateAccount", [IMPERSONATED_ADDRESS])

    # Initialize contract
    l2_message_receiver = w3.eth.contract(
        address=L2_MESSAGE_RECEIVER_ADDRESS, abi=l2_message_receiver_abi
    )

    # Prepare config struct
    config = {
        "gateway": "0x3c2269811836af69497E5F486A85D7316753cf62",
        "sender": "0x2Efd4430489e1a05A89c2f51811aC661B7E5FF84",
        "senderChainId": 101,
    }

    print("config", config)

    # Build transaction
    nonce = w3.eth.get_transaction_count(IMPERSONATED_ADDRESS)

    tx = l2_message_receiver.functions.setParams(
        "0x092baadb7def4c3981454dd9c0a0d7ff07bcfc86", config
    ).build_transaction(
        {
            "from": IMPERSONATED_ADDRESS,
            "nonce": nonce,
            "gas": 2000000,  # Adjust gas as needed
            "gasPrice": w3.eth.gas_price,
        }
    )

    # Sign and send transaction
    # Note: In a local network with impersonated account,
    # you might need to handle signing differently
    signed_tx = w3.eth.account.sign_transaction(
        tx,
        private_key="YOUR_PRIVATE_KEY_HERE",  # You'll need the private key for the impersonated account
    )
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(")")

    # Stop impersonating
    w3.provider.make_request("hardhat_stopImpersonatingAccount", [IMPERSONATED_ADDRESS])


if __name__ == "__main__":
    import asyncio

    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
