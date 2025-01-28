from web3 import Web3
import json
import time

web3 = Web3(Web3.HTTPProvider("<WEB3_PROVIDER>"))

private_key = "<PRIVATE_KEY>"
account = web3.eth.account.from_key(private_key)
web3.eth.default_account = account.address


def load_abi(path_to_abi):
    with open(path_to_abi, "r") as file:
        return json.load(file)


def get_nonce():
    l2_message_receiver_abi = load_abi("<PATH_TO_L2_MESSAGE_RECEIVER_ABI>")

    l2_message_receiver_address = "0xc37ff39e5a50543ad01e42c4cd88c2939dd13002"

    l2_message_receiver = web3.eth.contract(
        address=Web3.to_checksum_address(l2_message_receiver_address),
        abi=l2_message_receiver_abi,
    )

    nonce = l2_message_receiver.functions.nonce().call()
    print(nonce)


def get_gas_price_with_buffer(web3, buffer_percentage=10):
    """Get current gas price and add a buffer percentage."""
    current_gas_price = web3.eth.gas_price
    buffer = current_gas_price * buffer_percentage // 100
    return current_gas_price + buffer


def wait_for_transaction(web3, tx_hash, timeout=120):
    """Wait for transaction to be mined and return the transaction receipt."""
    start_time = time.time()
    while True:
        try:
            tx_receipt = web3.eth.get_transaction_receipt(tx_hash)
            if tx_receipt is not None:
                return tx_receipt
        except Exception as e:
            print(f"Error checking transaction receipt: {e}")

        if time.time() - start_time > timeout:
            raise TimeoutError(f"Transaction not mined after {timeout} seconds")

        time.sleep(2)


def retry_payload(chain_id, remote_address, local_address, payload, gas_limit=500000):
    """Retry a LayerZero payload with better error handling and monitoring."""
    try:
        lz_endpoint_abi = load_abi("<PATH_TO_LZ_ENDPOINT_ABI>")
        lz_endpoint_address = "0x6098e96a28E02f27B1e6BD381f870F1C8Bd169d3"

        lz_endpoint = web3.eth.contract(
            address=Web3.to_checksum_address(lz_endpoint_address), abi=lz_endpoint_abi
        )

        remote_and_local = Web3.solidityKeccak(
            ["address", "address"], [remote_address, local_address]
        )

        # Get gas price with 10% buffer
        gas_price = get_gas_price_with_buffer(web3, 10)

        tx = lz_endpoint.functions.retryPayload(
            chain_id, remote_and_local, payload
        ).build_transaction(
            {
                "from": web3.eth.default_account,
                "nonce": web3.eth.get_transaction_count(web3.eth.default_account),
                "gas": gas_limit,
                "gasPrice": gas_price,
            }
        )

        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        print(f"Transaction sent: {tx_hash.hex()}")

        # Wait for transaction receipt
        tx_receipt = wait_for_transaction(web3, tx_hash)

        if tx_receipt["status"] == 1:
            print("Transaction successfully mined!")
            print(f"Gas used: {tx_receipt['gasUsed']}")
        else:
            print("Transaction failed!")

        return tx_receipt

    except Exception as e:
        print(f"Error in retry_payload: {e}")
        raise


def main():
    get_nonce()

    # Example usage of the new retry_payload function
    remote_address = "0xeec0df0991458274ff0ede917e9827ffc67a8332"
    local_address = "0xc37ff39e5a50543ad01e42c4cd88c2939dd13002"
    payload = "0x000000000000000000000000901f2d23823730fb7f2356920e0e273efdcdfe1700000000000000000000000000000000000000000000000322994640a6175555"
    chain_id = "10161"

    receipt = retry_payload(
        chain_id=chain_id,
        remote_address=remote_address,
        local_address=local_address,
        payload=payload,
    )

    print(f"Transaction receipt: {receipt}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
