from web3 import Web3
import json
import os
from typing import Optional


def get_web3(network: str = "local") -> Web3:
    """
    Get Web3 instance based on network
    """
    if network == "local":
        return Web3(Web3.HTTPProvider("http://localhost:8545"))
    elif network == "arbitrum_goerli":
        # You should use environment variables for RPC URLs in production
        return Web3(Web3.HTTPProvider(os.getenv("ARBITRUM_GOERLI_RPC_URL")))
    else:
        raise ValueError(f"Unsupported network: {network}")


def load_abi(filename: str) -> dict:
    """
    Load ABI from artifacts directory
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, f"../artifacts/contracts/{filename}")) as f:
        return json.load(f)["abi"]


def impersonate_account(w3: Web3, address: str):
    """
    Impersonate an account on local network
    """
    w3.provider.make_request("hardhat_impersonateAccount", [address])


def stop_impersonating(w3: Web3, address: str):
    """
    Stop impersonating an account
    """
    w3.provider.make_request("hardhat_stopImpersonatingAccount", [address])
