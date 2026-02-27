#qorsan73
import asyncio
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def setup_headless_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.binary_location = "/usr/bin/chromium"
    
    service = Service(executable_path="/usr/bin/chromedriver")
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"{RED}[!] Error launching browser: {e}{RESET}")
        return None

def check_breaches(email):
    print(f"\n{CYAN}[*] Checking Data Breaches for: {email}...{RESET}"
    try:
        url = f"https://api.proxynova.com/comb?query={email}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and response.json().get("count", 0) > 0:
            print(f"{RED}[!] ALERT: This email was found in {response.json()['count']} breaches!{RESET}")
            return response.json().get("lines", [])
        print(f"{GREEN}[✓] No major public breaches found.{RESET}")
    except:
        print(f"{YELLOW}[!] Breach check failed (Connection issue).{RESET}")
    return []

def check_and_screenshot(username):
    folder_name = f"Evidence_{username}"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    driver = setup_headless_browser()
    if not driver: return [], folder_name
    
    print(f"\n{CYAN}[*] Investigating: '{username}' & Capturing Evidence...{RESET}")
    
    platforms = {
        "Instagram": "https://www.instagram.com/",
        "Twitter": "https://twitter.com/",
        "GitHub": "https://github.com/",
        "Facebook": "https://www.facebook.com/",
        "TikTok": "https://www.tiktok.com/@",
        "Reddit": "https://www.reddit.com/user/"
    }
    
    results = []
    for name, base_url in platforms.items():
        url = f"{base_url}{username}"
        try:
            driver.get(url)
            time.sleep(3)
            
            page_content = driver.page_source.lower()
            if any(x in page_content for x in ["404", "not found", "doesn't exist"]):
                print(f"{RED}[✗] {name}: Not found.{RESET}")
            else:
                screenshot_path = os.path.join(folder_name, f"{name}.png")
                driver.save_screenshot(screenshot_path)
                print(f"{GREEN}[✓] {name}: Found! Screenshot saved.{RESET}")
                results.append(f"{name}: {url}")
        except:
            print(f"{YELLOW}[!] {name}: Skip due to error.{RESET}")
            
    driver.quit()
    return results, folder_name

async def main():
    os.system('clear')
    print(f"{CYAN}=============================================")
    print("    OSINT EVIDENCE COLLECTOR v2.0 (Kali-PRO)      ")
    print("    Developer: #qorsan73                     ")
    print("============================================={RESET}")
    
    target = input("\n[+] Enter Target Email: ").strip()
    if not target or "@" not in target:
        print(f"{RED}[!] Please enter a valid email.{RESET}")
        return

    username = target.split('@')[0]
    
    breaches = check_breaches(target)
    
    start_time = time.time()
    found_profiles, folder = check_and_screenshot(username)
    end_time = time.time()
    
    print(f"\n{CYAN}--- Investigation Finished ---{RESET}")
    print(f"Evidence Folder: {os.path.abspath(folder)}")
    
    with open(os.path.join(folder, "Full_Report.txt"), "w") as f:
        f.write(f"OSINT REPORT FOR: {target}\n")
        f.write(f"Breaches Found: {len(breaches)}\n")
        f.write("-" * 30 + "\nProfiles:\n" + "\n".join(found_profiles))
        if breaches:
            f.write("\n\nBreach Data (Sample):\n" + "\n".join(breaches[:10]))
            
    print(f"{GREEN}[✓] Full Report generated: {folder}/Full_Report.txt{RESET}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{RED}[!] Tool stopped.{RESET}")
