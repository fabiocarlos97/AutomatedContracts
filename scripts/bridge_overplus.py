from web3 import Web3
from eth_account.account import Account
from eth_typing import Address

# ABI for the Distribution contract - you'll need to add this
DISTRIBUTION_ABI = [
    # Add relevant ABI entries for overplus(), bridgeOverplus(), etc.
]

def wei(amount: str) -> int:
    """Convert ETH amount to wei"""
    return Web3.to_wei(amount, 'ether')

async def main():
    # Connect to local network
    w3 = Web3(Web3.HTTPProvider('http://localhost:3000'))
    
    # Setup accounts
    owner_address = '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'
    signer_address = '0x1FE04BC15Cf2c5A2d41a0b3a96725596676eBa1E'
    
    # Impersonate accounts (assuming using Hardhat network)
    w3.provider.make_request("hardhat_impersonateAccount", [owner_address])
    w3.provider.make_request("hardhat_impersonateAccount", [signer_address])
    w3.provider.make_request("softhat_impersonateAccount", [signer_address])

    
    # Send some ETH to signer
    tx = {
        'from': owner_address,
        'to': signer_address,
        'value': wei('0.1'),
        'gas': 21000,
        'gasPrice': w3.eth.gas_price
    }
    w3.eth.send_transaction(tx)
    
    # Contract addresses
    distribution_address = '0x47176B2Af9885dC6C4575d4eFd63895f7Aaa4790'
    
    # Create contract instance
    distribution = w3.eth.contract(
        address=distribution_address,
        abi=DISTRIBUTION_ABI
    )
    
    # Get overplus
    overplus = await distribution.functions.overplus().call()
    print(overplus)
    
    # Bridge overplus
    tx = distribution.functions.bridgeOverplus(
        100000,
        60000000,
        100000000000000
    ).build_transaction({
        'from': owner_address,
        'value': 200000000000000,
        'gas': 300000,  # Adjust as needed
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(owner_address)
    })
    
    # Send transaction
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=owner_private_key)  # You'll need the private key
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    # Get new overplus value
    overplus = await distribution.functions.overplus().call()
    print(overplus)
    
    print(')')

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 