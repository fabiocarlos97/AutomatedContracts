from web3 import Web3

# Connect to Ethereum node (replace with your node URL)
w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"))

# Contract address and ABI (replace with actual ABI)
contract_address = "0x2C0f43E5C92459F62C102517956A95E88E177e95"
contract_abi = [
    {
        "constant": False,
        "inputs": [
            {"name": "amount", "type": "uint256"},
            {"name": "destination", "type": "uint256"}
        ],
        "name": "swap",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Load contract
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Set up account (replace with actual private key and address)
private_key = "YOUR_PRIVATE_KEY"
account = w3.eth.account.from_key(private_key)

# Check balance before swap
balance = contract.functions.balanceOf().call()
print(f"Current contract balance: {balance}")

# Swap tokens
swap_amount = 500
destination = 0

nonce = w3.eth.get_transaction_count(account.address)
tx = contract.functions.swap(swap_amount, destination).build_transaction({
    "from": account.address,
    "gas": 200000,
    "gasPrice": w3.to_wei("10", "gwei"),
    "nonce": nonce
})

# Sign and send transaction
signed_tx = w3.eth.account.sign_transaction(tx, private_key)
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
print(f"Transaction sent! Hash: {tx_hash.hex()}")

# Wait for transaction receipt
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Transaction confirmed:", receipt)
