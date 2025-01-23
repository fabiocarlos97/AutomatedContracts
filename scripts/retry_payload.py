from web3 import Web3
import json

web3 = Web3(Web3.HTTPProvider('<WEB3_PROVIDER>'))

private_key = '<PRIVATE_KEY>'
account = web3.eth.account.from_key(private_key)
web3.eth.default_account = account.address

def load_abi(path_to_abi):
    with open(path_to_abi, 'r') as file:
        return json.load(file)

def get_nonce():
    l2_message_receiver_abi = load_abi('<PATH_TO_L2_MESSAGE_RECEIVER_ABI>')
    
    l2_message_receiver_address = '0xc37ff39e5a50543ad01e42c4cd88c2939dd13002'

    l2_message_receiver = web3.eth.contract(
        address=Web3.to_checksum_address(l2_message_receiver_address),
        abi=l2_message_receiver_abi
    )

    nonce = l2_message_receiver.functions.nonce().call()
    print(nonce)

def main():
    get_nonce()

    lz_endpoint_abi = load_abi('<PATH_TO_LZ_ENDPOINT_ABI>')
    
    lz_endpoint_address = '0x6098e96a28E02f27B1e6BD381f870F1C8Bd169d3'

    lz_endpoint = web3.eth.contract(
        address=Web3.to_checksum_address(lz_endpoint_address),
        abi=lz_endpoint_abi
    )

    remote_and_local = Web3.solidityKeccak(
        ['address', 'address'],
        ['0xeec0df0991458274ff0ede917e9827ffc67a8332', '0xc37ff39e5a50543ad01e42c4cd88c2939dd13002']
    )

    payload = '0x000000000000000000000000901f2d23823730fb7f2356920e0e273efdcdfe1700000000000000000000000000000000000000000000000322994640a6175555'
    chain_id = '10161'

    tx = lz_endpoint.functions.retryPayload(chain_id, remote_and_local, payload).build_transaction({
        'from': web3.eth.default_account,
        'nonce': web3.eth.get_transaction_count(web3.eth.default_account),
        'gas': 500000,
        'gasPrice': web3.to_wei('5', 'gwei')
    })

    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    print(f'Transaction sent: {tx_hash.hex()}')

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
