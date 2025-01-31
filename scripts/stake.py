from web3 import Web3
import json
import logging

logging.basicConfig(level=logging.INFO)

NODE_URL = "http://127.0.0.1:8545"
SIGNER_ADDRESS = "0x040EF6Fb6592A70291954E2a6a1a8F320FF10626"
DISTRIBUTION_CONTRACT_ADDRESS = "0x2e1fF173085A5ef12046c27E442f12f79A0092b7"
LIBRARY_ADDRESS = "0x7431aDa8a591C955a994a21710752EF9b882b8e3"
PRIVATE_KEY = "0x2e1fF173085A5ef12046c27E442f12f79A0092b7"

with open("distribution_abi.json", "r") as file:
    DISTRIBUTION_ABI = json.load(file)

w3 = Web3(Web3.HTTPProvider(NODE_URL))
assert w3.is_connected(), "Failed to connect to Ethereum node"

account = w3.eth.account.from_key(PRIVATE_KEY)
assert account.address.lower() == SIGNER_ADDRESS.lower(), "Private key does not match the signer address"

distribution_contract = w3.eth.contract(address=DISTRIBUTION_CONTRACT_ADDRESS, abi=DISTRIBUTION_ABI)

def stake(pool_id: int, amount: int):
    try:
        tx = distribution_contract.functions.stake(pool_id, amount).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 200000,
            'gasPrice': w3.to_wei('10', 'gwei')
        })

        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        logging.info(f"Staking successful: {receipt.transactionHash.hex()}")
    except Exception as e:
        logging.error(f"Error while staking: {e}")

if __name__ == "__main__":
    stake(0, 1000000000000000000)
