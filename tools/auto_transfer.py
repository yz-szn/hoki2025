import json
import os
import asyncio
from web3 import Web3
from colorama import init, Fore, Style
from utils.logger import log

init(autoreset=True)

# ABI Standar ERC-20
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "success", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

def load_data():
    try:
        with open("data/rpc.json", "r") as file:
            rpc_list = json.load(file)
        with open("data/wallet_pengirim.json", "r") as file:
            wallet_pengirim = json.load(file)
        with open("data/wallet_penerima.json", "r") as file:
            wallet_penerima = json.load(file)
        with open("data/ERC20.json", "r") as file:  # Load ERC20 contract address
            erc20_data = json.load(file)
            token_contract_address = erc20_data[0]["Contract_Address"]
        return rpc_list, wallet_pengirim, wallet_penerima, token_contract_address
    except Exception as e:
        log("AUTO TRANSFER", f"Gagal memuat data: {e}", "ERROR")
        return None, None, None, None

async def transfer_native_token(w3, wallet_pengirim, wallet_penerima, amount, rpc_info):
    try:
        nonce = w3.eth.get_transaction_count(wallet_pengirim["address"])
        gas_price = w3.eth.gas_price
        gas_limit = 21000  # Gas limit untuk transfer native token

        tx = {
            'nonce': nonce,
            'to': wallet_penerima["address"],
            'value': w3.to_wei(amount, 'ether'),
            'gas': gas_limit,
            'gasPrice': gas_price,
            'chainId': rpc_info["chain_id"]
        }

        signed_tx = w3.eth.account.sign_transaction(tx, wallet_pengirim["privateKey"])
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        log("AUTO TRANSFER", f"Transfer native token berhasil! Hash: {tx_hash.hex()}", "SUCCESS")
        return True
    except Exception as e:
        log("AUTO TRANSFER", f"Gagal melakukan transfer native token: {e}", "ERROR")
        return False

async def transfer_custom_token(w3, wallet_pengirim, wallet_penerima, amount, rpc_info, token_contract_address):
    try:
        # Load token contract menggunakan ABI standar ERC-20
        token_contract = w3.eth.contract(address=token_contract_address, abi=ERC20_ABI)

        # Get token decimals
        decimals = token_contract.functions.decimals().call()
        token_amount = int(amount * (10 ** decimals))

        # Get nonce
        nonce = w3.eth.get_transaction_count(wallet_pengirim["address"])

        # Build transaction
        tx = token_contract.functions.transfer(
            wallet_penerima["address"],
            token_amount
        ).build_transaction({
            'chainId': rpc_info["chain_id"],
            'gas': 200000,  # Adjust gas limit as needed
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce,
        })

        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(tx, wallet_pengirim["privateKey"])
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        log("AUTO TRANSFER", f"Transfer token berhasil! Hash: {tx_hash.hex()}", "SUCCESS")
        return True
    except Exception as e:
        log("AUTO TRANSFER", f"Gagal melakukan transfer token: {e}", "ERROR")
        return False

async def run():
    rpc_list, wallet_pengirim, wallet_penerima, token_contract_address = load_data()
    if not rpc_list or not wallet_pengirim or not wallet_penerima or not token_contract_address:
        return

    # Pilih jenis transfer
    print(Fore.YELLOW + "\n[=== PILIH JENIS TRANSFER ===]")
    print(Fore.CYAN + "1. Kirim Native Token (ETH/BNB)")
    print(Fore.CYAN + "2. Kirim Token Lain (ERC-20/BEP-20)")
    choice = input(Fore.GREEN + "Masukkan pilihan (1/2): ").strip()

    if choice not in ["1", "2"]:
        log("AUTO TRANSFER", "Pilihan tidak valid! Mohon pilih 1 atau 2.", "ERROR")
        return

    amount = float(input(Fore.WHITE + "Masukkan jumlah yang akan ditransfer: ").strip())
    if amount <= 0:
        log("AUTO TRANSFER", "Jumlah transfer harus lebih dari 0!", "ERROR")
        return

    # Gunakan RPC pertama dalam daftar
    rpc_info = rpc_list[0]
    w3 = Web3(Web3.HTTPProvider(rpc_info["rpc_endpoint"]))
    if not w3.is_connected():
        log("AUTO TRANSFER", f"Gagal terhubung ke RPC: {rpc_info['rpc_endpoint']}", "ERROR")
        return

    log("AUTO TRANSFER", f"Terhubung ke RPC: {rpc_info['network_name']}", "INFO")

    if choice == "1":
        log("AUTO TRANSFER", f"Memulai transfer {amount} native token dari {wallet_pengirim['address']} ke {wallet_penerima['address']}", "INFO")
        success = await transfer_native_token(w3, wallet_pengirim, wallet_penerima, amount, rpc_info)
    elif choice == "2":
        log("AUTO TRANSFER", f"Memulai transfer {amount} token dari {wallet_pengirim['address']} ke {wallet_penerima['address']}", "INFO")
        success = await transfer_custom_token(w3, wallet_pengirim, wallet_penerima, amount, rpc_info, token_contract_address)

    if not success:
        log("AUTO TRANSFER", "Transfer gagal!", "ERROR")

if __name__ == "__main__":
    asyncio.run(run())