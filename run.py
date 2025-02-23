import os
import sys
import asyncio
from tools import auto_transfer, create_wallet, scanproxy, walmeBOT
from utils.logger import log
from colorama import init, Fore, Style

init(autoreset=True)

def welcome():
    print(
        f"""
        {Fore.GREEN + Style.BRIGHT}
         /$$   /$$ /$$$$$$$$        /$$$$$$$ /$$$$$$$$ /$$$$$$$             
        | $$  | $$|____ /$$/       /$$_____/|____ /$$/| $$__  $$            
        | $$  | $$   /$$$$/       |  $$$$$$    /$$$$/ | $$  \ $$            
        | $$  | $$  /$$__/         \____  $$  /$$__/  | $$  | $$           
        |  $$$$$$$ /$$$$$$$$       /$$$$$$$/ /$$$$$$$$| $$  | $$           
         \____  $$|________/      |_______/ |________/|__/  |__/           
        /$$  | $$ ______________________________________________                                                     
       |  $$$$$$/ ============ Nothing's Impossible !! =========                                       
        \______/
        """
    )

welcome()
print(f"{Fore.CYAN}{'=' * 18}")
print(Fore.CYAN + "#### WalmeBOT ####")
print(f"{Fore.CYAN}{'=' * 18}")

async def main():
    while True:
        print(Fore.YELLOW + "\n[=== PILIH MENU ===]")
        print(Fore.CYAN + "1. Create Wallet")
        print(Fore.CYAN + "2. Auto Transfer")
        print(Fore.CYAN + "3. Scan Proxy")
        print(Fore.CYAN + "4. WalmeBOT")
        print(Fore.CYAN + "5. Keluar")

        choice = input(Fore.GREEN + "Masukkan pilihan (1-5): ").strip()

        if choice == "1":
            print(Fore.BLUE + "Memulai proses create wallet...")
            await create_wallet.run()
        elif choice == "2":
            print(Fore.BLUE + "Memulai proses auto transfer...")
            await auto_transfer.run()
        elif choice == "3":
            print(Fore.BLUE + "Memulai proses scan proxy...")
            await scanproxy.run()
        elif choice == "4":
            print(Fore.BLUE + "Menjalankan WalmeBOT...")
            walmeBOT.main()
        elif choice == "5":
            print(Fore.RED + "Keluar dari program...")
            return
        else:
            print(Fore.RED + "Pilihan tidak valid! Mohon pilih antara 1-5.")

if __name__ == "__main__":
    asyncio.run(main())