import asyncio
import aiohttp
import re
import os
from colorama import init, Fore, Style
from datetime import datetime
import time
from aiohttp_socks import ProxyConnector
from utils.logger import log

init(autoreset=True)

proxy_sources = [
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/refs/heads/main/proxies/protocols/socks5/data.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/refs/heads/main/proxies/all.txt",
    "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/refs/heads/master/socks5.txt"
]

output_file = "data/proxywork.txt"
SEMAPHORE_LIMIT = 20  
semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)

working_count = 0
not_working_count = 0
total_checked = 0

async def fetch_proxies():
    proxies = set()
    log("SCAN PROXY", "Mengambil daftar proxy dari berbagai sumber...", "INFO")

    async with aiohttp.ClientSession() as session:
        for url in proxy_sources:
            try:
                async with session.get(url, timeout=10) as response:
                    response.raise_for_status()
                    new_proxies = set(line.strip() for line in (await response.text()).splitlines() if line.strip())
                    proxies.update(new_proxies)
                    log("SCAN PROXY", f"Berhasil mengambil {len(new_proxies)} proxy dari {url}", "SUCCESS")
            except Exception as e:
                log("SCAN PROXY", f"Gagal mengambil proxy dari {url}: {e}", "ERROR")

    log("SCAN PROXY", f"Total proxy ditemukan: {len(proxies)}", "INFO")
    return list(proxies)

async def check_proxy(proxy):
    global working_count, not_working_count, total_checked

    cleaned_proxy = proxy.strip()
    if not cleaned_proxy:
        return

    match = re.match(r'^(?:(http|socks5|socks4)://)?([^:]+):(\d+)$', cleaned_proxy, re.IGNORECASE)
    if not match:
        log("SCAN PROXY", f"Format proxy tidak valid: {cleaned_proxy}", "ERROR")
        return

    proto = match.group(1) or "socks5"  
    ip, port = match.group(2), match.group(3)
    proxy_url = f"{proto}://{ip}:{port}"

    async with semaphore:
        try:
            connector = ProxyConnector.from_url(proxy_url) if "socks" in proto else None

            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get("https://httpbin.org/ip", timeout=5) as response:
                    if response.status == 200:
                        working_count += 1
                        with open(output_file, "a") as file:
                            file.write(f"{proxy_url}\n")
                        status = True
                    else:
                        not_working_count += 1
                        status = False
        except Exception:
            not_working_count += 1
            status = False

        total_checked += 1
        waktu_sekarang = datetime.now().strftime("%d/%m/%Y %H:%M WIB")
        proxy_color = Fore.GREEN if status else Fore.RED
        log_message = f"{proxy_color}{proxy_url}{Style.RESET_ALL}"
        log("SCAN PROXY", log_message, "INFO" if status else "ERROR")

        await asyncio.sleep(0.1)

async def run():
    await main()

async def main():
    global working_count, not_working_count, total_checked
    start_time = time.time()

    if os.path.exists(output_file):
        open(output_file, "w").close()

    log("SCAN PROXY", "Pilih opsi:", "INFO")
    print(f"{Fore.CYAN}1. Auto Proxy (Ambil dari sumber publik)")
    print(f"{Fore.CYAN}2. Private Proxy (Ambil dari file proxy.txt)")
    pilihan = input(f"{Fore.WHITE}Masukkan pilihan (1/2): ").strip()

    if pilihan == "1":
        proxies = await fetch_proxies()
    elif pilihan == "2":
        if os.path.exists("data/proxy.txt"):
            with open("data/proxy.txt", "r") as file:
                proxies = list(set(file.read().splitlines())) 
            log("SCAN PROXY", f"Berhasil memuat {len(proxies)} proxy dari proxy.txt", "SUCCESS")
        else:
            log("SCAN PROXY", "File proxy.txt tidak ditemukan!", "ERROR")
            return
    else:
        log("SCAN PROXY", "Pilihan tidak valid!", "ERROR")
        return

    if proxies:
        log("SCAN PROXY", f"Total proxy yang akan dicek: {len(proxies)}", "INFO")
        tasks = [check_proxy(proxy) for proxy in proxies]
        await asyncio.gather(*tasks)

        log("SCAN PROXY", "Proxy checking complete!", "INFO")
        log("SCAN PROXY", f"Total proxy yang work: {working_count}", "SUCCESS")
        log("SCAN PROXY", f"Total proxy yang not work: {not_working_count}", "ERROR")

        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            log("SCAN PROXY", f"Proxy yang berhasil tersimpan di '{output_file}'", "SUCCESS")
        else:
            log("SCAN PROXY", "Tidak ada proxy yang berhasil.", "ERROR")

    end_time = time.time()
    duration = end_time - start_time
    log("SCAN PROXY", f"Waktu pemrosesan: {duration:.2f} detik", "INFO")

if __name__ == "__main__":
    asyncio.run(main())