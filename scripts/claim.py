from web3 import Web3
from eth_account import Account
from web3.middleware import geth_poa_middleware

def wei(amount):
    return Web3.toWei(amount, 'ether')

async def main():
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    owner_address = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    signer_address = "0x1FE04BC15Cf2c5A2d41a0b3a96725596676eBa1E"
    owner = w3.eth.account.privateKeyToAccount(owner_address)
    signer = w3.eth.account.privateKeyToAccount(signer_address)

    tx = {
        'to': signer.address,
        'value': wei(0.1),
        'gas': 21000,
        'gasPrice': w3.toWei('20', 'gwei'),
        'nonce': w3.eth.getTransactionCount(owner.address),
    }
    signed_tx = owner.signTransaction(tx)
    w3.eth.sendRawTransaction(signed_tx.rawTransaction)

    address = "0x47176B2Af9885dC6C4575d4eFd63895f7Aaa4790"
    distribution = w3.eth.contract(address=address)

    tx = distribution.functions.claim(4, signer.address).buildTransaction({
        'value': wei(0.01),
        'from': signer.address,
        'nonce': w3.eth.getTransactionCount(signer.address),
        'gas': 200000,
        'gasPrice': w3.toWei('20', 'gwei'),
    })
    signed_tx = signer.signTransaction(tx)
    w3.eth.sendRawTransaction(signed_tx.rawTransaction)

    print("Claim executed successfully")

if __name__ == "__main__":
    try:
        import asyncio
        asyncio.run(main())
    except Exception as error:
        print(f"Error: {error}")
