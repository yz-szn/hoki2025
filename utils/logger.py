import datetime
from colorama import init, Fore, Style

init(autoreset=True)

COLORS = {
    "CREATE WALLET": Fore.GREEN, 
    "AUTO TRANSFER": Fore.GREEN,  
    "SCAN PROXY": Fore.GREEN,
    "WalmeBOT": Fore.GREEN,
    "INFO": Fore.GREEN,
    "SUCCESS": Fore.GREEN,  
    "ERROR": Fore.RED,  
    "WARN": Fore.YELLOW,  
    "TIMESTAMP": Fore.CYAN,  
    "ADDRESS": Fore.WHITE, 
    "ACCOUNT": Fore.WHITE
}

def log(action, message, level):
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    
    color_action = COLORS.get(action, Style.RESET_ALL)
    color_level = COLORS.get(level, Style.RESET_ALL)
    color_time = COLORS["TIMESTAMP"]
    color_address = COLORS["ADDRESS"]

    log_message = (
        f"{color_action}[ {action} ]{Style.RESET_ALL} "
        f"{color_time}[ {timestamp} ]{Style.RESET_ALL} "
        f"{color_level}[ {level} ]{Style.RESET_ALL} "
        f"{color_address}{message}{Style.RESET_ALL}"
    )
    
    print(log_message)