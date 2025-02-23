import json
from web3 import Web3
from mnemonic import Mnemonic
from eth_account import Account
from colorama import init, Fore, Style
from utils.logger import log

init(autoreset=True)

Account.enable_unaudited_hdwallet_features()

def generate_wallets(count):
    wallets = []
    mnemo = Mnemonic("english")

    for _ in range(count):
        mnemonic = mnemo.generate(strength=128)
        account = Account.from_mnemonic(mnemonic)

        wallet = {
            "address": account.address,
            "privateKey": account.key.hex(),
            "mnemonic": mnemonic
        }
        wallets.append(wallet)
    
    return wallets

def save_wallets(wallets, filename="data/wallet_baru.json"):
    with open(filename, "w") as file:
        json.dump(wallets, file, indent=4)
    log("CREATE WALLET", f"Wallet berhasil disimpan di {filename}", "SUCCESS")

async def run():
    log("CREATE WALLET", "Membuat wallet baru...", "INFO")
    count = int(input(f"{Fore.WHITE}Masukkan jumlah wallet yang ingin dibuat: ").strip())
    
    if count <= 0:
        log("CREATE WALLET", "Jumlah wallet harus lebih dari 0!", "ERROR")
        return

    wallets = generate_wallets(count)
    save_wallets(wallets)
    log("CREATE WALLET", f"Berhasil membuat {count} wallet!", "SUCCESS")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())