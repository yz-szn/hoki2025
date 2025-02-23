import os
import requests
import time
from colorama import Fore, Style, init
from fake_useragent import UserAgent
from utils.logger import log 

init(autoreset=True)

def read_tokens(file_path):
    if not os.path.exists(file_path):
        log("WalmeBOT", "File token.txt not found!", "ERROR")
        return []
    
    with open(file_path, 'r') as file:
        tokens = file.read().splitlines()
    
    return tokens

def read_proxies(file_path):
    if not os.path.exists(file_path):
        log("WalmeBOT", "File proxy.txt not found. Running without proxy.", "WARN")
        return []
    
    with open(file_path, 'r') as file:
        proxies = file.read().splitlines()
    
    if not proxies:
        log("WalmeBOT", "File proxy.txt is empty. Running without proxy.", "WARN")
    
    return proxies

def write_proxies(file_path, proxies):
    with open(file_path, 'w') as file:
        for proxy in proxies:
            file.write(proxy + "\n")

def add_used_proxy(proxy):
    used_proxy_path = os.path.join("data", "used_proxy.txt")
    with open(used_proxy_path, "a") as file:
        file.write(proxy + "\n")

def generate_random_headers(token=None):
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Accept': 'application/json',
        'Accept-Language': 'id-ID,id;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://waitlist.walme.io/',
        'Origin': 'https://waitlist.walme.io',
        'Sec-Ch-Ua': '"Not(A:Brand";v="99", "Brave";v="133", "Chromium";v="133"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Linux"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Gpc': '1',
        'Priority': 'u=1, i'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
    return headers

def fetch_profile(token, headers, proxy=None):
    url = "https://api.walme.io/user/profile"
    headers['Authorization'] = f'Bearer {token}'
    
    try:
        response = requests.get(url, headers=headers, proxies={"http": proxy, "https": proxy} if proxy else None, timeout=10)
        
        if response.status_code == 200:
            log("WalmeBOT", "Successfully fetched profile data!", "SUCCESS")
            return response.json()
        else:
            log("WalmeBOT", f"Failed to fetch profile data. Status code: {response.status_code}", "ERROR")
            return None
    except requests.exceptions.RequestException as e:
        log("WalmeBOT", f"Error fetching profile data: {e}", "ERROR")
        return None

def display_profile(profile_data):
    log("WalmeBOT", f"Name: {profile_data.get('name')}", "INFO")
    log("WalmeBOT", f"Username: {profile_data.get('display_name')}", "INFO")
    log("WalmeBOT", f"Email: {profile_data.get('email')}", "INFO")
    log("WalmeBOT", f"Matrix User: {profile_data.get('matrix_user')}", "INFO")
    log("WalmeBOT", f"Referral Code: {profile_data.get('referral_code')}", "INFO")
    log("WalmeBOT", f"Total XP: {profile_data.get('reward')}", "INFO")
    log("WalmeBOT", f"Referral Reward: {profile_data.get('reward_ref')}", "INFO")
    log("WalmeBOT", f"Total Referral: {profile_data.get('total_ref')}", "INFO")

    identities = profile_data.get('identities', [])
    telegram = next((identity.get('auth_name') for identity in identities if identity.get('auth_provider') == 'telegram'), 'N/A')
    discord = next((identity.get('auth_name') for identity in identities if identity.get('auth_provider') == 'discord'), 'N/A')
    twitter = next((identity.get('auth_name') for identity in identities if identity.get('auth_provider') == 'twitter'), 'N/A')
    
    log("WalmeBOT", f"Telegram: {telegram}", "INFO")
    log("WalmeBOT", f"Discord: {discord}", "INFO")
    log("WalmeBOT", f"Twitter: {twitter}", "INFO")
    log("WalmeBOT", f"Last Login: {profile_data.get('last_login')}", "INFO")
    log("WalmeBOT", f"Created: {profile_data.get('created_at')}", "INFO")

def fetch_all_tasks(token, headers, proxy=None):
    url = "https://api.walme.io/waitlist/tasks"
    headers['Authorization'] = f'Bearer {token}'
    
    try:
        response = requests.get(url, headers=headers, proxies={"http": proxy, "https": proxy} if proxy else None, timeout=10)
        
        if response.status_code == 200:
            log("WalmeBOT", "Successfully fetched tasks!", "SUCCESS")
            return response.json()
        else:
            log("WalmeBOT", f"Failed to fetch tasks. Status code: {response.status_code}", "ERROR")
            return None
    except requests.exceptions.RequestException as e:
        log("WalmeBOT", f"Error fetching tasks: {e}", "ERROR")
        return None

def extract_all_tasks(tasks):
    all_tasks = []
    for task in tasks:
        all_tasks.append(task)
        if 'child' in task and task['child']:
            all_tasks.extend(extract_all_tasks(task['child']))
    return all_tasks

def complete_task(task_id, token, headers, proxy=None):
    url = f"https://api.walme.io/waitlist/tasks/{task_id}"
    headers['Authorization'] = f'Bearer {token}'
    data = {}
    
    try:
        response = requests.patch(url, headers=headers, json=data, proxies={"http": proxy, "https": proxy} if proxy else None, timeout=10)
        
        if response.status_code == 200:
            log("WalmeBOT", f"Successfully completed task {task_id}!", "SUCCESS")
            return response.json()
        else:
            log("WalmeBOT", f"Failed to complete task {task_id}. Status code: {response.status_code}", "ERROR")
            return None
    except requests.exceptions.RequestException as e:
        log("WalmeBOT", f"Error completing task: {e}", "ERROR")
        return None

def countdown_timer(seconds):
    while seconds:
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        timer = f"{hours:02d}:{mins:02d}:{secs:02d}"
        print(f"Countdown {timer}", end="\r")
        time.sleep(1)
        seconds -= 1
    print()

def main():
    tokens = read_tokens('data/token.txt')
    
    if not tokens:
        return
    
    proxies = read_proxies('data/proxy.txt')
    account_headers = {}
    loop_duration = 24 * 3600
    
    while True:
        for idx, token in enumerate(tokens):
            log("WalmeBOT", f"Processing account {idx + 1}...", "INFO")
            if token not in account_headers:
                account_headers[token] = generate_random_headers(token)
            
            headers = account_headers[token]
            proxy_index = idx % len(proxies)
            success = False
            
            while not success:
                proxy = proxies[proxy_index]
                log("WalmeBOT", f"Trying proxy: {proxy}", "INFO")
                profile_data = fetch_profile(token, headers, proxy)
                
                if profile_data:
                    display_profile(profile_data)
                    tasks = fetch_all_tasks(token, headers, proxy)
                    if tasks:
                        all_tasks = extract_all_tasks(tasks)
                        incomplete_tasks = [task for task in all_tasks if task.get('status') in ['new', 'started']]
                        
                        if not incomplete_tasks:
                            log("WalmeBOT", "No incomplete tasks found.", "INFO")
                            success = True
                            break
                        for task in incomplete_tasks:
                            task_id = task.get('id')
                            task_title = task.get('title')
                            task_status = task.get('status')
                            
                            log("WalmeBOT", f"Processing task: {task_title} (ID: {task_id}, Status: {task_status})", "INFO")
                            
                            if task_status in ['new', 'started']:
                                task_response = complete_task(task_id, token, headers, proxy)
                                
                                if task_response:
                                    log("WalmeBOT", "Task Response:", "INFO")
                                    log("WalmeBOT", f"Task ID: {task_response.get('id')}", "INFO")
                                    log("WalmeBOT", f"Title: {task_response.get('title')}", "INFO")
                                    log("WalmeBOT", f"Status: {task_response.get('status')}", "INFO")
                                    log("WalmeBOT", f"Reward: {task_response.get('reward')} XP", "INFO")
                                    log("WalmeBOT", f"Started At: {task_response.get('started_at')}", "INFO")
                                    log("WalmeBOT", f"Completed At: {task_response.get('completed_at')}", "INFO")
                                log("WalmeBOT", "Waiting for 10 seconds before processing the next task...", "INFO")
                                time.sleep(10)
                            else:
                                log("WalmeBOT", "Task already completed. Skipping...", "INFO")
                        
                        success = True
                        add_used_proxy(proxy)
                        proxy_index = (proxy_index + 1) % len(proxies)
                    else:
                        log("WalmeBOT", "Failed to fetch tasks. Trying next proxy...", "ERROR")
                else:
                    log("WalmeBOT", "Failed to fetch profile data. Trying next proxy...", "ERROR")
                proxy_index = (proxy_index + 1) % len(proxies)
            if not success:
                log("WalmeBOT", "All proxies failed for this account. Moving to the next account.", "ERROR")
            log("WalmeBOT", "━" * 50 + "\n", "INFO")
        countdown_timer(loop_duration)

if __name__ == "__main__":
    main()