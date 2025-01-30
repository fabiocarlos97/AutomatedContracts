from web3 import Web3
from solcx import compile_source
import json

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
assert w3.is_connected(), "Failed to connect to Ethereum node."

wst_eth = "0x5979D7b546E38E414F7E9822514be443A4800529"
signer_address = "0x151c2b49CdEC10B150B2763dF3d1C00D70C90956"
contract_address = "0x47176b2af9885dc6c4575d4efd63895f7aaa4790"
private_key = "<YOUR_PRIVATE_KEY>"

with open("L2TokenReceiverV2_abi.json", "r") as f:
    contract_abi = json.load(f)

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

nonce = w3.eth.get_transaction_count(signer_address)

tx = contract.functions.withdrawToken(
    signer_address, wst_eth, 729987493896647493703
).build_transaction({
    "chainId": 1337,
    "gas": 500000,
    "gasPrice": w3.to_wei("10", "gwei"),
    "nonce": nonce,
})

signed_tx = w3.eth.account.sign_transaction(tx, private_key)

tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
print(f"Transaction sent! Hash: {tx_hash.hex()}")

receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Transaction confirmed in block {receipt.blockNumber}")
