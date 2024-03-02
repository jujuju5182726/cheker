from eth_keys import keys
import aiohttp
import asyncio
import os
import time

async def get_eth_balance(session, address, api_key):
    url = f'https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={api_key}'
    retry_count = 3  # Number of retry attempts
    for attempt in range(retry_count):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    balance = int(data['result']) / 10**18  # Convert wei to Ether
                    return balance
                else:
                    print(f"Error checking balance for {address}: {response.status}")
                    return None
        except aiohttp.client_exceptions.ClientOSError as e:
            if "ServerDisconnectedError" in str(e):  # Check if the error is ServerDisconnectedError
                print("Server disconnected. Retrying...")
            else:
                print(f"Connection error: {e}")
            if attempt < retry_count - 1:
                print(f"Retrying... Attempt {attempt + 1}/{retry_count}")
                await asyncio.sleep(120)  # Wait for 5 seconds before retrying
            else:
                print("Max retry attempts reached. Exiting.")
                return None

async def check_wallets(api_key):
    wallets_checked = 0
    wallets_found = 0

    async with aiohttp.ClientSession() as session:
        while wallets_found < 2:  # Change the condition based on the number of wallets you want to find
            private_key_bytes = os.urandom(32)
            private_key = keys.PrivateKey(private_key_bytes)
            public_key = private_key.public_key
            address = public_key.to_checksum_address()
            wallets_checked += 1
            print(f"Wallets Checked: {wallets_checked}, Wallets Found: {wallets_found}", end="\r")

            balance = await get_eth_balance(session, address, api_key)
            if balance is not None:
                if balance > 0:
                    wallets_found += 1
                    print(f"\nWallet with balance found! ({wallets_found} found in {wallets_checked} checked)")
                    with open(f"found_wallet_{wallets_found}.txt", "w") as file:
                        file.write(f"Private Key: {private_key.to_hex()}\n")
                        file.write(f"Public Key: {public_key.to_hex()}\n")
                        file.write(f"Address: {address}\n")
                        file.write(f"Balance: {balance} ETH\n")

async def run_with_asyncio():
    api_keys = ['79NE2HM482ZECC38MZNS365D1JNUGSMKFT',
                'XTPR4ZTV8RPTSN5SDR6SFCCWSS4TIN7K9N',
                'D3D4H3ICHVCVAH2X3X41ZJFTZCV1CJI4J5',
                '269INYF49BTCCYQXGK2ZASHYID71UD1AHI',
                'T6IWE2MWYEYACN429N3A5DV2E7RMNBFDM6',
                'QWRZYXI36SMB1XGQGGPEXANAZ9RF9VBHUU',
                ]  # Add additional API keys here

    await asyncio.gather(*[check_wallets(api_key) for api_key in api_keys])

asyncio.run(run_with_asyncio())
