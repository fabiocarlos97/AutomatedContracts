from web3 import Web3
from decimal import Decimal

# Extended ERC20 ABI to include symbol and decimals
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    }
]

async def main():
    # Connect to Arbitrum Goerli
    w3 = Web3(Web3.HTTPProvider('https://goerli-rollup.arbitrum.io/rpc'))
    
    # Addresses
    user = '0xb6067C1B07e3Fe12d18C11a0cc6F1366BD70EC95'  # token receiver
    token_address = '0x87726993938107d9B9ce08c99BDde8736D899a5D'  # wStETH
    
    # Create contract instance
    token = w3.eth.contract(
        address=token_address,
        abi=ERC20_ABI
    )
    
    # Get token info
    symbol = await token.functions.symbol().call()
    decimals = await token.functions.decimals().call()
    balance = await token.functions.balanceOf(user).call()
    
    # Format balance
    formatted_balance = Decimal(balance) / Decimal(10 ** decimals)
    
    print(f"Token: {symbol} ({token_address})")
    print(f"Balance of {user}: {formatted_balance} {symbol}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 