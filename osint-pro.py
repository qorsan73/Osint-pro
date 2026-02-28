# Developer: #qorsan73
import os
import time
import random
import requests
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

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
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () =>营造 undefined})")
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
    
    print(f"{CYAN}[*] Starting Full Investigation on: {username}{RESET}")
    print(f"{YELLOW}[!] Folder Created: {folder_name}{RESET}\n")

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
        report.write(f"OSINT-PRO INVESTIGATION REPORT - : {username}\n")
        report.write(f"Date: {datetime.datetime.now()}\n" + "="*40 + "\n\n")

        for name, base_url in platforms.items():
            url = f"{base_url}{username}"
            print(f"{CYAN}[>] Checking {name}...{RESET}")
            
            try:
                arch_url, timestamp = check_archive(username, base_url)
                
                is_live = False
                if driver:
                    driver.get(url)
                    time.sleep(2)
                    if "404" not in driver.title and "Not Found" not in driver.page_source:
                        is_live = True
                        screenshot_path = os.path.join(folder_name, f"{name}_Live.png")
                        driver.save_screenshot(screenshot_path)
                        print(f"{GREEN}[✓] {name}: LIVE FOUND & SCREENSHOT SAVED{RESET}")
                status = f"Platform: {name}\nURL: {url}\nLive: {is_live}\n"
                if arch_url:
                    status += f"Archive: {arch_url} (Date: {timestamp})\n"
                    print(f"{YELLOW}[∞] {name}: Archive found!{RESET}")
                
                if is_live or arch_url:
                    report.write(status + "-"*20 + "\n")
                    results.append(name)
                else:
                    print(f"{RED}[✗] {name}: No data found.{RESET}")

            except Exception as e:
                print(f"{RED}[!] Error checking {name}{RESET}")
            time.sleep(random.uniform(1.5, 3.0))

    if driver: driver.quit()
    return folder_name, results

if __name__ == "__main__":
    os.system('clear' if os.name != 'nt' else 'cls')
    print(f"{CYAN}=============================================")
    print("    ULTIMATE STEALTH INVESTIGATOR v1.0       ")
    print("    By : qorsan taez                         ")
    print("============================================={RESET}")

    target_input = input("\n[+] Enter Target Username/Email: ").strip()
    if target_input:
        folder, found = start_investigation(target_input)
        print(f"\n{GREEN}[✓] Investigation Finished!{RESET}")
        print(f"{CYAN}[i] Results saved in: {os.path.abspath(folder)}{RESET}")
        print(f"{CYAN}[i] Total Platforms Found: {len(found)}{RESET}")

