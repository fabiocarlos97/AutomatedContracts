from web3 import Web3
from utils import get_web3, load_abi
from decimal import Decimal

# Contract addresses
POOL_ADDRESS = (
    "0x7a5EA63E2491d32A101774C4e5b0E7C04ADf4F3a"  # Update with your pool address
)
L2_MESSAGE_RECEIVER_ADDRESS = "0x2C0f43E5C92459F62C102517956A95E88E177e95"


def format_token_amount(amount: int, decimals: int = 18) -> str:
    """
    Format token amount from wei to human readable format
    """
    return str(Decimal(amount) / Decimal(10**decimals))


async def main():
    w3 = get_web3("arbitrum_goerli")

    # Load contract ABIs
    pool_abi = load_abi("UniswapV3Pool.sol/UniswapV3Pool.json")
    position_manager_abi = load_abi(
        "NonfungiblePositionManager.sol/NonfungiblePositionManager.json"
    )

    # Initialize contracts
    pool = w3.eth.contract(address=POOL_ADDRESS, abi=pool_abi)

    # Get pool state
    slot0 = pool.functions.slot0().call()
    current_tick = slot0[1]
    sqrt_price_x96 = slot0[0]

    print(f"Current Pool State:")
    print(f"Current Tick: {current_tick}")
    print(f"SqrtPriceX96: {sqrt_price_x96}")

    # Get position details for token ID 86416
    position_id = 86416
    position = pool.functions.positions(position_id).call()

    print(f"\nPosition {position_id} Details:")
    print(f"Liquidity: {position[0]}")
    print(f"Lower Tick: {position[1]}")
    print(f"Upper Tick: {position[2]}")

    # Calculate fees earned
    fees_token0 = position[3]
    fees_token1 = position[4]

    print(f"\nFees Earned:")
    print(f"Token0 Fees: {format_token_amount(fees_token0)} tokens")
    print(f"Token1 Fees: {format_token_amount(fees_token1)} tokens")


if __name__ == "__main__":
    import asyncio

    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
