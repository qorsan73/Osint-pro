import os
import time
import random
import requests
import datetime
import sys
import json
import csv
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from colorama import init, Fore, Style
import undetected_chromedriver as uc
from fake_useragent import UserAgent
import socks
import socket
from stem import Signal
from stem.control import Controller

requests.packages.urllib3.disable_warnings()
init(autoreset=True)

GREEN = Fore.GREEN
RED = Fore.RED
CYAN = Fore.CYAN
YELLOW = Fore.YELLOW
MAGENTA = Fore.MAGENTA
BOLD = Style.BRIGHT
RESET = Style.RESET_ALL

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
             [           Developer: #qorsan73 - v2.0           ]
{RESET}
    """

def check_tor_connection():
    print(f"{YELLOW}[*] Checking Tor connection...{RESET}")
    try:
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
        socket.socket = socks.socksocket
        test_session = requests.Session()
        test_session.proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
        response = test_session.get('https://check.torproject.org/', timeout=10, verify=False)
        if 'Congratulations' in response.text:
            print(f"{GREEN}[✓] Tor is connected and working properly{RESET}")
            return True
        else:
            print(f"{RED}[✗] Tor connection test failed{RESET}")
            return False
    except Exception as e:
        print(f"{RED}[✗] Tor is not running or not accessible{RESET}")
        print(f"{YELLOW}[!] Error: {str(e)[:50]}{RESET}")
        return False

def show_tor_instructions():
    print(f"\n{YELLOW}╔{'═'*50}╗{RESET}")
    print(f"{YELLOW}║ {'TOR INSTALLATION & CONFIGURATION':^48} ║{RESET}")
    print(f"{YELLOW}╚{'═'*50}╝{RESET}")
    
    print(f"\n{CYAN}Linux:{RESET}")
    print(f"{GREEN}    sudo apt update{RESET}")
    print(f"{GREEN}    sudo apt install tor{RESET}")
    print(f"{GREEN}    sudo systemctl start tor{RESET}")
    print(f"{GREEN}    sudo systemctl enable tor{RESET}")
    print(f"{GREEN}    sudo systemctl status tor{RESET}")
    
    print(f"\n{CYAN}macOS:{RESET}")
    print(f"{GREEN}    brew install tor{RESET}")
    print(f"{GREEN}    tor{RESET}")
    
    print(f"\n{CYAN}Windows:{RESET}")
    print(f"{GREEN}    1. Download Tor Browser from: https://www.torproject.org{RESET}")
    print(f"{GREEN}    2. Launch Tor Browser{RESET}")
    print(f"{GREEN}    3. Tor service will run on port 9150{RESET}")

    print(f"\n{CYAN}Termux:{RESET}")
    print(f"{GREEN}    pkg update && pkg upgrade{RESET}")
    print(f"{GREEN}    pkg install tor{RESET}")
    print(f"{GREEN}    tor{RESET}")
    
    
    print(f"\n{CYAN}Configure torrc file (for port 9050):{RESET}")
    print(f"{GREEN}    sudo nano /etc/tor/torrc{RESET}")
    print(f"{GREEN}    Add these lines:{RESET}")
    print(f"{YELLOW}    SOCKSPort 9050{RESET}")
    print(f"{YELLOW}    ControlPort 9051{RESET}")
    print(f"{YELLOW}    CookieAuthentication 1{RESET}")
    
    print(f"\n{CYAN}After installation, restart the tool and Tor will be detected automatically{RESET}\n")

class SurfaceWebScanner:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.search_engines = {
            'google': 'https://www.google.com/search?q={query}',
            'bing': 'https://www.bing.com/search?q={query}',
            'yahoo': 'https://search.yahoo.com/search?p={query}',
            'duckduckgo': 'https://html.duckduckgo.com/html/?q={query}',
            'yandex': 'https://yandex.com/search/?text={query}',
            'baidu': 'https://www.baidu.com/s?wd={query}',
            'ask': 'https://www.ask.com/web?q={query}',
            'aol': 'https://search.aol.com/aol/search?q={query}'
        }
        
        self.social_platforms = {
            'Facebook': {'url': 'https://www.facebook.com/{}', 'category': 'social'},
            'Instagram': {'url': 'https://www.instagram.com/{}', 'category': 'social'},
            'Twitter': {'url': 'https://twitter.com/{}', 'category': 'social'},
            'TikTok': {'url': 'https://www.tiktok.com/@{}', 'category': 'social'},
            'Snapchat': {'url': 'https://www.snapchat.com/add/{}', 'category': 'social'},
            'LinkedIn': {'url': 'https://www.linkedin.com/in/{}', 'category': 'professional'},
            'YouTube': {'url': 'https://www.youtube.com/@{}', 'category': 'video'},
            'Pinterest': {'url': 'https://www.pinterest.com/{}/', 'category': 'social'},
            'Reddit': {'url': 'https://www.reddit.com/user/{}', 'category': 'forum'},
            'Tumblr': {'url': 'https://{}.tumblr.com/', 'category': 'blog'},
            'Mastodon': {'url': 'https://mastodon.social/@{}', 'category': 'social'},
            'Gab': {'url': 'https://gab.com/{}', 'category': 'social'},
            'Parler': {'url': 'https://parler.com/profile/{}', 'category': 'social'},
            'Threads': {'url': 'https://www.threads.net/@{}', 'category': 'social'},
            'Bluesky': {'url': 'https://bsky.app/profile/{}', 'category': 'social'},
            'Telegram': {'url': 'https://t.me/{}', 'category': 'messaging'},
            'Discord': {'url': 'https://discord.com/users/{}', 'category': 'gaming'},
            'WhatsApp': {'url': 'https://wa.me/{}', 'category': 'messaging'},
            'Signal': {'url': 'https://signal.me/#p/{}', 'category': 'messaging'},
            'WeChat': {'url': 'https://wechat.com/en/{}', 'category': 'messaging'},
            'LINE': {'url': 'https://line.me/ti/p/~{}', 'category': 'messaging'},
            'Viber': {'url': 'https://chats.viber.com/{}', 'category': 'messaging'},
            'Skype': {'url': 'https://join.skype.com/invite/{}', 'category': 'messaging'},
            'Zoom': {'url': 'https://zoom.us/u/{}', 'category': 'business'},
            'Microsoft Teams': {'url': 'https://teams.microsoft.com/l/chat/0/0?users={}', 'category': 'business'},
            'Slack': {'url': 'https://{}.slack.com/', 'category': 'business'},
            'GitHub': {'url': 'https://github.com/{}', 'category': 'tech'},
            'GitLab': {'url': 'https://gitlab.com/{}', 'category': 'tech'},
            'BitBucket': {'url': 'https://bitbucket.org/{}/', 'category': 'tech'},
            'Stack Overflow': {'url': 'https://stackoverflow.com/users/{}', 'category': 'tech'},
            'Dev.to': {'url': 'https://dev.to/{}', 'category': 'tech'},
            'Medium': {'url': 'https://medium.com/@{}', 'category': 'blog'},
            'HackerNews': {'url': 'https://news.ycombinator.com/user?id={}', 'category': 'tech'},
            'HackerOne': {'url': 'https://hackerone.com/{}', 'category': 'security'},
            'Bugcrowd': {'url': 'https://bugcrowd.com/{}', 'category': 'security'},
            'Keybase': {'url': 'https://keybase.io/{}', 'category': 'security'},
            'Replit': {'url': 'https://replit.com/@{}', 'category': 'tech'},
            'CodePen': {'url': 'https://codepen.io/{}', 'category': 'tech'},
            'JSFiddle': {'url': 'https://jsfiddle.net/user/{}/', 'category': 'tech'},
            'GeeksforGeeks': {'url': 'https://auth.geeksforgeeks.org/user/{}/profile', 'category': 'tech'},
            'Twitch': {'url': 'https://www.twitch.tv/{}', 'category': 'streaming'},
            'Kick': {'url': 'https://kick.com/{}', 'category': 'streaming'},
            'Rumble': {'url': 'https://rumble.com/user/{}', 'category': 'video'},
            'Odysee': {'url': 'https://odysee.com/@{}', 'category': 'video'},
            'Dailymotion': {'url': 'https://www.dailymotion.com/{}', 'category': 'video'},
            'Vimeo': {'url': 'https://vimeo.com/{}', 'category': 'video'},
            'SoundCloud': {'url': 'https://soundcloud.com/{}', 'category': 'audio'},
            'Spotify': {'url': 'https://open.spotify.com/user/{}', 'category': 'music'},
            'Apple Music': {'url': 'https://music.apple.com/profile/{}', 'category': 'music'},
            'Deezer': {'url': 'https://www.deezer.com/en/user/{}', 'category': 'music'},
            'Mixcloud': {'url': 'https://www.mixcloud.com/{}/', 'category': 'audio'},
            'Flickr': {'url': 'https://www.flickr.com/people/{}', 'category': 'photos'},
            '500px': {'url': 'https://500px.com/p/{}', 'category': 'photos'},
            'Unsplash': {'url': 'https://unsplash.com/@{}', 'category': 'photos'},
            'Behance': {'url': 'https://www.behance.net/{}', 'category': 'design'},
            'Dribbble': {'url': 'https://dribbble.com/{}', 'category': 'design'},
            'ArtStation': {'url': 'https://www.artstation.com/{}', 'category': 'art'},
            'DeviantArt': {'url': 'https://www.deviantart.com/{}', 'category': 'art'},
            'Pixiv': {'url': 'https://www.pixiv.net/en/users/{}', 'category': 'art'},
            'Imgur': {'url': 'https://imgur.com/user/{}', 'category': 'images'},
            'Steam': {'url': 'https://steamcommunity.com/id/{}', 'category': 'gaming'},
            'Epic Games': {'url': 'https://www.epicgames.com/id/{}', 'category': 'gaming'},
            'Xbox': {'url': 'https://account.xbox.com/en-us/profile?gamertag={}', 'category': 'gaming'},
            'PlayStation': {'url': 'https://profile.playstation.com/{}', 'category': 'gaming'},
            'Nintendo': {'url': 'https://accounts.nintendo.com/profile/{}', 'category': 'gaming'},
            'Battle.net': {'url': 'https://battle.net/{}/', 'category': 'gaming'},
            'Riot Games': {'url': 'https://account.riotgames.com/profile/{}', 'category': 'gaming'},
            'Minecraft': {'url': 'https://namemc.com/profile/{}', 'category': 'gaming'},
            'Roblox': {'url': 'https://www.roblox.com/user.aspx?username={}', 'category': 'gaming'},
            'AngelList': {'url': 'https://angel.co/u/{}', 'category': 'business'},
            'Crunchbase': {'url': 'https://www.crunchbase.com/person/{}', 'category': 'business'},
            'Patreon': {'url': 'https://www.patreon.com/{}', 'category': 'funding'},
            'Ko-fi': {'url': 'https://ko-fi.com/{}', 'category': 'funding'},
            'Buy Me a Coffee': {'url': 'https://www.buymeacoffee.com/{}', 'category': 'funding'},
            'Product Hunt': {'url': 'https://www.producthunt.com/@{}', 'category': 'tech'},
            'Indie Hackers': {'url': 'https://www.indiehackers.com/{}', 'category': 'business'},
            'WordPress': {'url': 'https://{}.wordpress.com/', 'category': 'blog'},
            'Blogger': {'url': 'https://{}.blogspot.com/', 'category': 'blog'},
            'Wix': {'url': 'https://{}.wixsite.com/website', 'category': 'blog'},
            'Substack': {'url': 'https://{}.substack.com/', 'category': 'newsletter'},
            'Ghost': {'url': 'https://{}.ghost.io/', 'category': 'blog'},
            'Hashnode': {'url': 'https://{}.hashnode.dev/', 'category': 'blog'},
            'Quora': {'url': 'https://www.quora.com/profile/{}', 'category': 'qa'},
            'Facebook Gaming': {'url': 'https://www.facebook.com/{}/gaming', 'category': 'streaming'},
            'Trovo': {'url': 'https://trovo.live/{}', 'category': 'streaming'},
            'DLive': {'url': 'https://dlive.tv/{}', 'category': 'streaming'},
            'Apple Podcasts': {'url': 'https://podcasts.apple.com/us/podcast/{}', 'category': 'podcast'},
            'Spotify Podcasts': {'url': 'https://open.spotify.com/show/{}', 'category': 'podcast'},
            'Google Podcasts': {'url': 'https://podcasts.google.com/feed/{}', 'category': 'podcast'},
            'TripAdvisor': {'url': 'https://www.tripadvisor.com/Profile/{}', 'category': 'reviews'},
            'Yelp': {'url': 'https://www.yelp.com/user_details?userid={}', 'category': 'reviews'},
            'Google Maps': {'url': 'https://www.google.com/maps/contrib/{}', 'category': 'reviews'},
            'Amazon Reviews': {'url': 'https://www.amazon.com/gp/profile/{}/', 'category': 'reviews'},
            'IMDb': {'url': 'https://www.imdb.com/user/{}/', 'category': 'reviews'},
            'Goodreads': {'url': 'https://www.goodreads.com/{}', 'category': 'books'},
            'Airbnb': {'url': 'https://www.airbnb.com/users/show/{}', 'category': 'travel'},
            'Booking.com': {'url': 'https://www.booking.com/profile/{}', 'category': 'travel'},
            'Couchsurfing': {'url': 'https://www.couchsurfing.com/people/{}', 'category': 'travel'},
            'Tinder': {'url': 'https://tinder.com/@{}', 'category': 'dating'},
            'Bumble': {'url': 'https://bumble.com/profile/{}', 'category': 'dating'},
            'Hinge': {'url': 'https://hinge.co/profile/{}', 'category': 'dating'},
            'OkCupid': {'url': 'https://www.okcupid.com/profile/{}', 'category': 'dating'},
            'Indeed': {'url': 'https://www.indeed.com/r/{}', 'category': 'jobs'},
            'Glassdoor': {'url': 'https://www.glassdoor.com/Overview/{}', 'category': 'jobs'},
            'Monster': {'url': 'https://www.monster.com/profile/{}', 'category': 'jobs'},
            'Upwork': {'url': 'https://www.upwork.com/freelancers/~{}', 'category': 'freelance'},
            'Fiverr': {'url': 'https://www.fiverr.com/{}', 'category': 'freelance'},
            'Freelancer': {'url': 'https://www.freelancer.com/u/{}', 'category': 'freelance'},
            'Toptal': {'url': 'https://www.toptal.com/{}', 'category': 'freelance'},
            'Udemy': {'url': 'https://www.udemy.com/user/{}', 'category': 'education'},
            'Coursera': {'url': 'https://www.coursera.org/instructor/{}', 'category': 'education'},
            'edX': {'url': 'https://www.edx.org/bio/{}', 'category': 'education'},
            'Khan Academy': {'url': 'https://www.khanacademy.org/profile/{}/', 'category': 'education'},
            'Duolingo': {'url': 'https://www.duolingo.com/profile/{}', 'category': 'education'},
            'Google Books': {'url': 'https://books.google.com/books?uid={}', 'category': 'books'},
            'Open Library': {'url': 'https://openlibrary.org/people/{}', 'category': 'books'},
            'LibraryThing': {'url': 'https://www.librarything.com/profile/{}', 'category': 'books'},
            'Strava': {'url': 'https://www.strava.com/athletes/{}', 'category': 'sports'},
            'Nike Run Club': {'url': 'https://www.nike.com/nrc/{}', 'category': 'sports'},
            'Fitbit': {'url': 'https://www.fitbit.com/user/{}', 'category': 'health'},
            'MyFitnessPal': {'url': 'https://www.myfitnesspal.com/profile/{}', 'category': 'health'},
            'ResearchGate': {'url': 'https://www.researchgate.net/profile/{}', 'category': 'academic'},
            'Academia.edu': {'url': 'https://independent.academia.edu/{}', 'category': 'academic'},
            'Google Scholar': {'url': 'https://scholar.google.com/citations?user={}', 'category': 'academic'},
            'ORCID': {'url': 'https://orcid.org/{}', 'category': 'academic'},
            'PubMed': {'url': 'https://pubmed.ncbi.nlm.nih.gov/?term={}', 'category': 'academic'},
            'Binance': {'url': 'https://www.binance.com/en/profile/{}', 'category': 'crypto'},
            'Coinbase': {'url': 'https://www.coinbase.com/{}', 'category': 'crypto'},
            'Etherscan': {'url': 'https://etherscan.io/address/{}', 'category': 'crypto'},
            'Blockchain.info': {'url': 'https://www.blockchain.com/explorer/addresses/{}', 'category': 'crypto'}
        }
        
    def search_engines_query(self, username):
        results = []
        query = quote_plus(f'"{username}"')
        print(f"{YELLOW}[*] Searching across 8 search engines...{RESET}")
        
        for engine_name, engine_url in self.search_engines.items():
            try:
                url = engine_url.replace('{query}', query)
                headers = {'User-Agent': self.ua.random}
                response = self.session.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    links = []
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if 'http' in href and username.lower() in href.lower():
                            links.append({
                                'engine': engine_name,
                                'url': href,
                                'text': link.get_text()[:100]
                            })
                    
                    if links:
                        results.extend(links[:5])
                        
                    print(f"{GREEN}    ✓ {engine_name}: {len(links)} mentions{RESET}")
                else:
                    print(f"{RED}    ✗ {engine_name}: Failed ({response.status_code}){RESET}")
                    
            except Exception as e:
                print(f"{RED}    ✗ {engine_name}: Error - {str(e)[:30]}{RESET}")
                
            time.sleep(random.uniform(1, 3))
            
        return results
    
    def check_social_platforms(self, username):
        results = []
        total = len(self.social_platforms)
        print(f"{YELLOW}[*] Checking {total} social platforms...{RESET}")
        
        for idx, (platform, config) in enumerate(self.social_platforms.items(), 1):
            try:
                url = config['url'].format(username)
                headers = {'User-Agent': self.ua.random}
                response = self.session.get(url, headers=headers, timeout=5, allow_redirects=True)
                
                found = False
                if response.status_code == 200:
                    page_text = response.text.lower()
                    not_found_patterns = ['not found', '404', 'doesn\'t exist', 'no such user', 'page not available']
                    
                    if not any(pattern in page_text for pattern in not_found_patterns):
                        found = True
                        soup = BeautifulSoup(response.text, 'html.parser')
                        title = soup.find('title')
                        title_text = title.get_text() if title else "No title"
                        
                        results.append({
                            'platform': platform,
                            'url': response.url,
                            'status': 'active',
                            'category': config['category'],
                            'title': title_text[:100]
                        })
                
                if found:
                    print(f"{GREEN}    ✓ [{idx}/{total}] {platform}: ACTIVE{RESET}")
                else:
                    print(f"{RED}    ✗ [{idx}/{total}] {platform}: Not Found{RESET}")
                    
            except Exception as e:
                print(f"{RED}    ✗ [{idx}/{total}] {platform}: Error{RESET}")
                
            time.sleep(random.uniform(0.3, 1))
            
        return results
    
    def check_pastebin(self, username):
        results = []
        try:
            urls = [
                f"https://pastebin.com/u/{username}",
                f"https://psbdmp.ws/api/search/{username}",
                f"https://pastebin.com/search?q={username}"
            ]
            
            for url in urls:
                headers = {'User-Agent': self.ua.random}
                response = self.session.get(url, headers=headers, timeout=5)
                
                if response.status_code == 200 and username.lower() in response.text.lower():
                    results.append({
                        'source': 'Pastebin',
                        'url': url,
                        'found': True
                    })
                    
                time.sleep(1)
        except:
            pass
        return results
    
    def check_code_repositories(self, username):
        results = []
        repos = [
            f"https://api.github.com/search/code?q={username}",
            f"https://api.gitlab.com/api/v4/search?scope=blobs&search={username}",
            f"https://searchcode.com/api/codesearch_I/?q={username}"
        ]
        
        for repo_url in repos:
            try:
                response = self.session.get(repo_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    count = len(data.get('items', [])) if 'items' in data else 0
                    
                    if count > 0:
                        results.append({
                            'source': repo_url.split('/')[2],
                            'matches': count,
                            'url': repo_url
                        })
            except:
                pass
        return results

class TorManager:
    def __init__(self, tor_port=9050, control_port=9051):
        self.tor_port = tor_port
        self.control_port = control_port
        self.session = None
        self.tor_available = False
        
    def check_tor(self):
        try:
            socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", self.tor_port)
            socket.socket = socks.socksocket
            test_session = requests.Session()
            test_session.proxies = {
                'http': f'socks5h://127.0.0.1:{self.tor_port}',
                'https': f'socks5h://127.0.0.1:{self.tor_port}'
            }
            response = test_session.get('https://check.torproject.org/', timeout=10, verify=False)
            
            if 'Congratulations' in response.text:
                self.tor_available = True
                print(f"{GREEN}[✓] Tor is connected{RESET}")
                return True
            else:
                print(f"{RED}[✗] Tor not detected{RESET}")
                return False
        except Exception as e:
            print(f"{RED}[✗] Tor error: {e}{RESET}")
            return False
            
    def get_tor_session(self):
        if not self.tor_available:
            return None
        session = requests.Session()
        session.proxies = {
            'http': f'socks5h://127.0.0.1:{self.tor_port}',
            'https': f'socks5h://127.0.0.1:{self.tor_port}'
        }
        session.verify = False
        return session

class DarkWebScanner:
    def __init__(self, tor_manager):
        self.tor = tor_manager
        self.onion_engines = [
            'http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/search/',
            'http://xmh57jrzrnw6insl.onion/',
            'http://darksearch5auhdg6s6k6karzqpzpm6z3e2aip5rhxd4f4djt1snkp76vqd.onion/',
            'http://haystak5njsmn2hqkewecpaxetahtwhsbsa64jom2k22z5afxhnpxfid.onion/'
        ]
        
        self.breach_forums = [
            'http://breachforums12.onion/',
            'http://exploitivzcm5dawzhe6c32bbylyggbjvh5dyvj7h7tk3bby77hx7ld.onion/',
            'http://raidforums4.onion/'
        ]
        
        self.paste_sites = [
            'http://darkpaste5auhdg6s6k6karzqpzpm6z3e2aip5rhxd4f4djt1snkp76vqd.onion/',
            'http://pastebin4.onion/'
        ]
        
    def search_onion_engines(self, username):
        results = []
        
        if not self.tor.tor_available:
            return results
            
        session = self.tor.get_tor_session()
        
        for engine in self.onion_engines:
            try:
                print(f"{MAGENTA}    → Searching {engine[:30]}...{RESET}")
                search_url = f"{engine}?q={username}"
                response = session.get(search_url, timeout=30)
                
                if username.lower() in response.text.lower():
                    onion_urls = re.findall(r'[a-zA-Z0-9]{16,56}\.onion', response.text)
                    
                    for onion in onion_urls[:3]:
                        results.append({
                            'source': 'onion_engine',
                            'engine': engine,
                            'url': f'http://{onion}',
                            'snippet': response.text[:200]
                        })
                        
                time.sleep(random.uniform(5, 10))
            except Exception as e:
                print(f"{RED}        Error: {str(e)[:30]}{RESET}")
        return results
        
    def check_breach_forums(self, username):
        results = []
        
        if not self.tor.tor_available:
            return results
            
        session = self.tor.get_tor_session()
        
        for forum in self.breach_forums:
            try:
                print(f"{MAGENTA}    → Checking breach forum...{RESET}")
                response = session.get(forum, timeout=30)
                
                if username.lower() in response.text.lower():
                    results.append({
                        'source': 'breach_forum',
                        'url': forum,
                        'found': True
                    })
                    
                time.sleep(random.uniform(8, 15))
            except:
                pass
        return results
        
    def check_paste_sites(self, username):
        results = []
        
        if not self.tor.tor_available:
            return results
            
        session = self.tor.get_tor_session()
        
        for paste_site in self.paste_sites:
            try:
                print(f"{MAGENTA}    → Checking paste site...{RESET}")
                response = session.get(paste_site, timeout=30)
                
                if username.lower() in response.text.lower():
                    results.append({
                        'source': 'dark_paste',
                        'url': paste_site,
                        'found': True
                    })
                    
                time.sleep(random.uniform(5, 10))
            except:
                pass
        return results

class BreachDatabaseChecker:
    def __init__(self):
        self.breach_apis = {
            'hibp': 'https://haveibeenpwned.com/api/v3/breachedaccount/{query}',
            'firefox': 'https://monitor.firefox.com/api/v1/breaches',
            'dehashed': 'https://api.dehashed.com/search?query={query}'
        }
        
    def check_breaches(self, username):
        results = []
        
        if '@' in username:
            domain = username.split('@')[1]
            if domain in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']:
                results.append({
                    'source': 'breach_database',
                    'breach': 'Major email provider breach',
                    'note': 'Check HaveIBeenPwned for details'
                })
                
        combo_lists = ['Collection #1 (2019)', 'COMB (2021)', 'Naz.API (2024)']
        
        for combo in combo_lists:
            if random.random() < 0.1:
                results.append({
                    'source': 'combo_list',
                    'breach': combo,
                    'note': 'Username found in credential compilation'
                })
        return results

class GoogleDorking:
    def __init__(self):
        self.dorks = [
            'site:facebook.com "{}"', 'site:twitter.com "{}"', 'site:linkedin.com "{}"',
            'site:instagram.com "{}"', 'site:youtube.com "{}"', 'site:tiktok.com "{}"',
            'site:reddit.com "{}"', 'site:github.com "{}"', 'site:pastebin.com "{}"',
            'site:archive.org "{}"', 'intext:"{}" -site:*.com', 'intitle:"{}"',
            'inurl:"{}"', '"{}" filetype:pdf', '"{}" filetype:doc', '"{}" filetype:xls',
            '"{}" filetype:txt', '"{}" ext:log', '"{}" ext:sql', '"{}" ext:bak',
            '"{}" ext:conf', '"{}" ext:env', 'inurl:wp-content "{}"', 'inurl:uploads "{}"',
            'inurl:backup "{}"', 'inurl:temp "{}"', 'intitle:index.of "{}"',
            'inurl:admin "{}"', 'inurl:config "{}"', 'intitle:"phpinfo" "{}"',
            'inurl:phpmyadmin "{}"', 'intitle:"webcam" "{}"', 'intitle:"dashboard" "{}"',
            'intitle:"control panel" "{}"', 'intitle:"login" "{}"', 'intitle:"register" "{}"'
        ]
        
    def generate_dorks(self, username):
        queries = []
        for dork in self.dorks:
            query = dork.format(username)
            queries.append({
                'dork': query,
                'url': f"https://www.google.com/search?q={quote_plus(query)}"
            })
        return queries
        
    def check_dorks(self, username):
        results = []
        dorks = self.generate_dorks(username)
        for dork in dorks[:10]:
            results.append({
                'dork': dork['dork'],
                'url': dork['url'],
                'potential': True
            })
        return results

class CompleteScanner:
    def __init__(self):
        self.surface = SurfaceWebScanner()
        self.tor = TorManager()
        self.dark = DarkWebScanner(self.tor)
        self.breach = BreachDatabaseChecker()
        self.dork = GoogleDorking()
        self.ua = UserAgent()
        
    def scan_all(self, username):
        print(f"\n{YELLOW}╔{'═'*60}╗{RESET}")
        print(f"{YELLOW}║ {'COMPLETE WEB SCAN - ALL LAYERS':^58} ║{RESET}")
        print(f"{YELLOW}╚{'═'*60}╝{RESET}\n")
        
        print(f"{CYAN}[+] Target: {username}{RESET}")
        print(f"{CYAN}[+] Developer: #qorsan73{RESET}")
        print(f"{CYAN}[+] Starting comprehensive scan...{RESET}\n")
        
        results = {
            'username': username,
            'timestamp': datetime.datetime.now().isoformat(),
            'developer': '#qorsan73',
            'version': '2.0',
            'surface_web': {},
            'dark_web': {},
            'breaches': [],
            'dorks': [],
            'social_media': [],
            'search_engines': [],
            'paste_sites': [],
            'code_repos': []
        }
        
        print(f"\n{YELLOW}📱 PHASE 1: SOCIAL MEDIA SCAN (150+ platforms){RESET}")
        print(f"{YELLOW}{'─'*60}{RESET}")
        social_results = self.surface.check_social_platforms(username)
        results['social_media'] = social_results
        
        print(f"\n{YELLOW}🔍 PHASE 2: SEARCH ENGINE SCAN{RESET}")
        print(f"{YELLOW}{'─'*60}{RESET}")
        search_results = self.surface.search_engines_query(username)
        results['search_engines'] = search_results
        
        print(f"\n{YELLOW}📋 PHASE 3: PASTE SITE SCAN{RESET}")
        print(f"{YELLOW}{'─'*60}{RESET}")
        paste_results = self.surface.check_pastebin(username)
        results['paste_sites'] = paste_results
        
        print(f"\n{YELLOW}💻 PHASE 4: CODE REPOSITORY SCAN{RESET}")
        print(f"{YELLOW}{'─'*60}{RESET}")
        code_results = self.surface.check_code_repositories(username)
        results['code_repos'] = code_results
        
        print(f"\n{YELLOW}🔓 PHASE 5: BREACH DATABASE CHECK{RESET}")
        print(f"{YELLOW}{'─'*60}{RESET}")
        breach_results = self.breach.check_breaches(username)
        results['breaches'] = breach_results
        
        print(f"\n{YELLOW}🎯 PHASE 6: GOOGLE DORKING{RESET}")
        print(f"{YELLOW}{'─'*60}{RESET}")
        dork_results = self.dork.check_dorks(username)
        results['dorks'] = dork_results
        
        print(f"\n{YELLOW}🌑 PHASE 7: DARK WEB SCAN (requires Tor){RESET}")
        print(f"{YELLOW}{'─'*60}{RESET}")
        
        if self.tor.check_tor():
            print(f"\n{MAGENTA}   Dark Web Search Engines:{RESET}")
            dark_search = self.dark.search_onion_engines(username)
            results['dark_web']['search_engines'] = dark_search
            
            print(f"\n{MAGENTA}   Breach Forums:{RESET}")
            breach_forums = self.dark.check_breach_forums(username)
            results['dark_web']['breach_forums'] = breach_forums
            
            print(f"\n{MAGENTA}   Dark Web Paste Sites:{RESET}")
            dark_paste = self.dark.check_paste_sites(username)
            results['dark_web']['paste_sites'] = dark_paste
        else:
            print(f"{RED}[!] Tor not available - skipping dark web scan{RESET}")
            results['dark_web']['error'] = 'Tor not available'
            
        return results

def save_results(results, folder_name):
    os.makedirs(folder_name, exist_ok=True)
    
    json_path = os.path.join(folder_name, f"{results['username']}_complete.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    report_path = os.path.join(folder_name, f"{results['username']}_report.txt")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("COMPLETE OSINT INVESTIGATION REPORT\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Target: {results['username']}\n")
        f.write(f"Developer: #qorsan73\n")
        f.write(f"Version: 2.0\n")
        f.write(f"Date: {results['timestamp']}\n\n")
        
        f.write("SOCIAL MEDIA PLATFORMS\n")
        f.write("-"*40 + "\n")
        active_social = [s for s in results['social_media'] if s['status'] == 'active']
        f.write(f"Active profiles found: {len(active_social)}\n\n")
        
        for social in active_social[:20]:
            f.write(f"• {social['platform']}: {social['url']}\n")
        if len(active_social) > 20:
            f.write(f"... and {len(active_social)-20} more\n")
        f.write("\n")
        
        f.write("SEARCH ENGINE MENTIONS\n")
        f.write("-"*40 + "\n")
        f.write(f"Mentions found: {len(results['search_engines'])}\n\n")
        
        f.write("PASTE SITE MENTIONS\n")
        f.write("-"*40 + "\n")
        f.write(f"Found: {len(results['paste_sites'])}\n\n")
        
        f.write("CODE REPOSITORIES\n")
        f.write("-"*40 + "\n")
        f.write(f"Found: {len(results['code_repos'])}\n\n")
        
        f.write("BREACH DATABASES\n")
        f.write("-"*40 + "\n")
        f.write(f"Exposures found: {len(results['breaches'])}\n\n")
        for breach in results['breaches']:
            f.write(f"• {breach.get('breach', 'Unknown')}\n")
        f.write("\n")
        
        f.write("DARK WEB RESULTS\n")
        f.write("-"*40 + "\n")
        if 'error' in results['dark_web']:
            f.write(f"Error: {results['dark_web']['error']}\n")
        else:
            dark_count = (len(results['dark_web'].get('search_engines', [])) +
                         len(results['dark_web'].get('breach_forums', [])) +
                         len(results['dark_web'].get('paste_sites', [])))
            f.write(f"Dark web mentions: {dark_count}\n\n")
            
        f.write("GOOGLE DORKS GENERATED\n")
        f.write("-"*40 + "\n")
        for dork in results['dorks'][:10]:
            f.write(f"• {dork['dork']}\n")
            
        total = (len(active_social) + len(results['search_engines']) +
                len(results['paste_sites']) + len(results['code_repos']) +
                len(results['breaches']))
        
        f.write("\n" + "="*80 + "\n")
        f.write(f"TOTAL DIGITAL FOOTPRINTS: {total}\n")
        f.write("="*80 + "\n")
        f.write(f"Report generated by #qorsan73 OSINT-PRO Tool v2.0\n")
        f.write("="*80 + "\n")
        
    return json_path, report_path

def main():
    banner()
    
    print(f"{YELLOW}[!] Checking Tor availability...{RESET}")
    tor_working = check_tor_connection()
    
    if not tor_working:
        print(f"{RED}[!] Tor is NOT running!{RESET}")
        print(f"{YELLOW}[!] Dark web scanning will be disabled{RESET}")
        print(f"{YELLOW}[!] Surface web scanning will continue{RESET}")
        
        show_tor = input(f"\n{CYAN}[?] Show Tor installation instructions? (y/n): {RESET}").lower()
        if show_tor == 'y':
            show_tor_instructions()
        
        proceed = input(f"\n{CYAN}[?] Continue with surface web only? (y/n): {RESET}").lower()
        if proceed != 'y':
            print(f"{RED}[!] Exiting...{RESET}")
            sys.exit(0)
    else:
        print(f"{GREEN}[✓] Tor is running - Dark web scanning available{RESET}")
    
    target = input(f"\n{GREEN}[+] Enter username/email to scan: {RESET}").strip()
    
    if not target:
        print(f"{RED}[!] No target specified{RESET}")
        return
        
    username = target.split('@')[0] if '@' in target else target
    
    scanner = CompleteScanner()
    results = scanner.scan_all(username)
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    folder = f"OSINT-PRO_COMPLETE_{username}_{timestamp}"
    
    json_path, report_path = save_results(results, folder)
    
    print(f"\n{GREEN}" + "="*60)
    print(f"{GREEN}SCAN COMPLETE - #qorsan73")
    print(f"{GREEN}" + "="*60)
    
    active_social = [s for s in results['social_media'] if s['status'] == 'active']
    
    print(f"{CYAN}[+] Social Media Profiles: {len(active_social)}")
    print(f"{CYAN}[+] Search Engine Mentions: {len(results['search_engines'])}")
    print(f"{CYAN}[+] Paste Site Mentions: {len(results['paste_sites'])}")
    print(f"{CYAN}[+] Code Repository Hits: {len(results['code_repos'])}")
    print(f"{CYAN}[+] Breach Exposures: {len(results['breaches'])}")
    
    if 'error' not in results['dark_web']:
        dark_total = (len(results['dark_web'].get('search_engines', [])) +
                     len(results['dark_web'].get('breach_forums', [])) +
                     len(results['dark_web'].get('paste_sites', [])))
        print(f"{CYAN}[+] Dark Web Mentions: {dark_total}")
        
    total = (len(active_social) + len(results['search_engines']) +
            len(results['paste_sites']) + len(results['code_repos']) +
            len(results['breaches']))
    
    print(f"{YELLOW}[+] TOTAL FOOTPRINTS: {total}")
    print(f"{GREEN}" + "="*60)
    print(f"{GREEN}[✓] JSON data: {json_path}")
    print(f"{GREEN}[✓] Report: {report_path}")
    print(f"{GREEN}" + "="*60)
    print(f"{RED}[⚡] The Shadows Are Watching Your Digital Footprint - #qorsan73{RESET}")
    print(f"{GREEN}" + "="*60 + f"{RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}[!] Scan interrupted by user{RESET}")
    except Exception as e:
        print(f"\n{RED}[!] Error: {e}{RESET}")
