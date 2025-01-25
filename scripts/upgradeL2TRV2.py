from web3 import Web3
from solcx import compile_source

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

wstEth = '0x5979D7b546E38E414F7E9822514be443A4800529'
weth = '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1'
l2TokenReceiverOldAddress = '0x47176B2Af9885dC6C4575d4eFd63895f7Aaa4790'
l2TokenReceiverV2Impl = '0x27353fFaDFD53538e8BDF81be7041C56CE2d5ae4'

first_swap_params = {
    'tokenIn': wstEth,
    'tokenOut': weth,
    'fee': 100,
    'sqrtPriceLimitX96': 0
}

signer_address = '0x151c2b49CdEC10B150B2763dF3d1C00D70C90956'
private_key = 'YOUR_PRIVATE_KEY_HERE'
signer = w3.eth.account.from_key(private_key)

L2TokenReceiverABI = l2TokenReceiverOldAddress
L2TokenReceiverV2ABI = l2TokenReceiverV2Impl

l2_token_receiver_old = w3.eth.contract(address=l2TokenReceiverOldAddress, abi=L2TokenReceiverABI)

print("l2TokenReceiverOld:", l2_token_receiver_old.address)
print("swapParams:", l2_token_receiver_old.functions.params().call())

print("Upgrading L2TokenReceiverV2...")
upgrade_tx = l2_token_receiver_old.functions.upgradeTo(l2TokenReceiverV2Impl).buildTransaction({
    'from': signer.address,
    'nonce': w3.eth.get_transaction_count(signer.address),
    'gas': 3000000
})
signed_upgrade_tx = w3.eth.account.sign_transaction(upgrade_tx, private_key)
w3.eth.send_raw_transaction(signed_upgrade_tx.rawTransaction)

l2_token_receiver = w3.eth.contract(address=l2TokenReceiverOldAddress, abi=L2TokenReceiverV2ABI)

print("Editing params...")
edit_params_tx = l2_token_receiver.functions.editParams(first_swap_params, True).buildTransaction({
    'from': signer.address,
    'nonce': w3.eth.get_transaction_count(signer.address),
    'gas': 3000000
})
signed_edit_params_tx = w3.eth.account.sign_transaction(edit_params_tx, private_key)
w3.eth.send_raw_transaction(signed_edit_params_tx.rawTransaction)

print("firstSwapParams:", l2_token_receiver.functions.firstSwapParams().call())
print("secondSwapParams:", l2_token_receiver.functions.secondSwapParams().call())

print("Done")
