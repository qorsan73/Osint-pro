#qorsan73
import asyncio
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def setup_headless_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1280,1024")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def check_and_screenshot(username):
    folder_name = f"Evidence_{username}"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    print(f"\n{CYAN}[*] Investigating: '{username}' & Collecting Evidence...{RESET}")
    driver = setup_headless_browser()
    
    platforms = {
        "Instagram": "https://www.instagram.com/",
        "Twitter": "https://twitter.com/",
        "GitHub": "https://github.com/",
        "Facebook": "https://www.facebook.com/",
        "TikTok": "https://www.tiktok.com/@",
        "Pinterest": "https://www.pinterest.com/",
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
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{CYAN}=============================================")
    print("    OSINT EVIDENCE COLLECTOR v1.0 (kali-PRO)      ")
    print("============================================={RESET}")
    
    target = input("\n[+] Enter Email or Username: ").strip()
    username = target.split('@')[0] if "@" in target else target
    
    start_time = time.time()
    found_profiles, folder = check_and_screenshot(username)
    end_time = time.time()
    
    print(f"\n{CYAN}--- Investigation Finished ---{RESET}")
    print(f"Time Taken: {int(end_time - start_time)} seconds")
    print(f"Evidence Folder: {os.path.abspath(folder)}")
    
    if found_profiles:
        with open(os.path.join(folder, "Report.txt"), "w") as f:
            f.write(f"Target: {username}\nFound Profiles:\n" + "\n".join(found_profiles))
        print(f"{GREEN}[✓] Full Report generated inside the folder.{RESET}")

if __name__ == "__main__":
    asyncio.run(main())

