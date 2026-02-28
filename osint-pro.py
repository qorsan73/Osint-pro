# Developer: #qorsan73
import os
import time
import random
import requests
import datetime
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
BLINK = "\033[5m"
RESET = "\033[0m"

def banner():
    os.system('clear' if os.name != 'nt' else 'cls')
    logo = f"""
{RED}
 ██████╗ ███████╗██╗███╗   ██╗████████╗      ██████╗ ██████╗  ██████╗ 
██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝      ██╔══██╗██╔══██╗██╔═══██╗
██║   ██║███████╗██║██╔██╗ ██║   ██║         ██████╔╝██████╔╝██║   ██║
██║   ██║╚════██║██║██║╚██╗██║   ██║         ██╔═══╝ ██╔══██╗██║   ██║
╚██████╔╝███████║██║██║ ╚████║   ██║    ██╗  ██║     ██║  ██║╚██████╔╝
 ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═╝  ╚═╝     ╚═╝  ╚═╝ ╚═════╝ 
{RESET}{CYAN}
             [  The Shadows Are Watching Your Digital Footprint  ]
             [           Developer: #qorsan73 - v1.0           ]
{RESET}
    """
    print(logo)

def typing_effect(text, color=CYAN, delay=0.03):
    for char in text:
        sys.stdout.write(color + char + RESET)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def setup_stealth_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(110, 122)}.0.0.0 Safari/537.36")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except:
        return None

def check_archive(username, platform_url):
    target_url = f"{platform_url}{username}"
    api_url = f"http://archive.org/wayback/available?url={target_url}"
    try:
        res = requests.get(api_url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data["archived_snapshots"]:
                snap = data["archived_snapshots"]["closest"]
                return snap["url"], snap["timestamp"]
    except: pass
    return None, None

def start_investigation(target):
    username = target.split('@')[0] if "@" in target else target
    folder_name = f"OSINT_{username}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}"
    if not os.path.exists(folder_name): os.makedirs(folder_name)
    
    report_path = os.path.join(folder_name, "All-investigation.txt")
    
    print(f"\n{RED}[!] INITIALIZING DEEP SCAN ON: {username}{RESET}")
    typing_effect("[...] Accessing Global Databases...", RED)
    time.sleep(1)

    platforms = {
        "Instagram": "https://www.instagram.com/",
        "Twitter": "https://twitter.com/",
        "GitHub": "https://github.com/",
        "Reddit": "https://www.reddit.com/user/",
        "TikTok": "https://www.tiktok.com/@",
        "Pastebin": "https://pastebin.com/u/",
        "Imgur": "https://imgur.com/user/"
    }

    driver = setup_stealth_browser()
    results = []

    with open(report_path, "w", encoding="utf-8") as report:
        report.write(f"OSINT-PRO DEEP INVESTIGATION - TARGET: {username}\n")
        report.write(f"TIMESTAMP: {datetime.datetime.now()}\n" + "="*50 + "\n\n")

        for name, base_url in platforms.items():
            url = f"{base_url}{username}"
            print(f"{YELLOW}[SCANNING] {name}...{RESET}", end="\r")
            
            try:
                arch_url, timestamp = check_archive(username, base_url)
                
                is_live = False
                if driver:
                    try:
                        driver.get(url)
                        time.sleep(2)
                        if "404" not in driver.title and "Not Found" not in driver.page_source:
                            is_live = True
                            screenshot_path = os.path.join(folder_name, f"{name}_Live.png")
                            driver.save_screenshot(screenshot_path)
                    except: pass
                
                if is_live:
                    print(f"{GREEN}[FOUND] {name}: LIVE TARGET DETECTED!{RESET}")
                elif arch_url:
                    print(f"{YELLOW}[GHOST] {name}: ARCHIVED DATA RECOVERED!{RESET}")
                else:
                    print(f"{RED}[CLEAN] {name}: No footprints found.{RESET}")

                status = f"Platform: {name}\nURL: {url}\nLive: {is_live}\n"
                if arch_url:
                    status += f"Archive: {arch_url} (Date: {timestamp})\n"
                
                if is_live or arch_url:
                    report.write(status + "-"*30 + "\n")
                    results.append(name)

            except Exception as e:
                print(f"{RED}[ERROR] Failed to probe {name}{RESET}")
            
            time.sleep(random.uniform(0.5, 1.5))

    if driver: driver.quit()
    return folder_name, results

if __name__ == "__main__":
    banner()
    typing_effect("[+] Enter the target's digital alias: ", YELLOW, 0.05)
    target_input = input(f"{BOLD}>> {RESET}").strip()
    
    if target_input:
        folder, found_results = start_investigation(target_input)
        print(f"\n{RED}" + "="*50)
        print(f"{RED}[☠] INVESTIGATION COMPLETE")
        print(f"{CYAN}[+] Evidence Secured in: {os.path.abspath(folder)}")
        print(f"{CYAN}[+] Vulnerabilities Exposed: {len(found_results)}")
        print(f"{RED}" + "="*50 + f"{RESET}")
    else:
        print(f"{RED}[!] No target specified. Exiting...{RESET}")

