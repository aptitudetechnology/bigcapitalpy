
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_URL = "http://simple.local:5000"  # Change to your running app's base URL
LOGIN_URL = BASE_URL + "/auth/login"     # Change to your login endpoint
USERNAME = "admin@bigcapitalpy.com"                  # Change to your username
PASSWORD = "admin123"               # Change to your password

visited = set()
broken_links = []

session = requests.Session()

def is_internal(url):
    return url.startswith(BASE_URL) or url.startswith("/")

def crawl(url):
    if url in visited or not is_internal(url):
        return
    full_url = urljoin(BASE_URL, url)
    visited.add(full_url)
    try:
        resp = session.get(full_url, timeout=10)
    except Exception as e:
        broken_links.append((full_url, f"Request error: {e}"))
        return
    if resp.status_code >= 400:
        broken_links.append((full_url, f"Status {resp.status_code}"))
        return
    soup = BeautifulSoup(resp.text, "html.parser")
    for link in soup.find_all("a", href=True):
        href = link["href"]
        # Ignore mailto, tel, javascript, etc.
        if href.startswith("mailto:") or href.startswith("tel:") or href.startswith("javascript:"):
            continue
        next_url = urljoin(full_url, href)
        # Only crawl internal links
        if urlparse(next_url).netloc == urlparse(BASE_URL).netloc:
            crawl(next_url)

if __name__ == "__main__":
    # 1. Log in first
    login_data = {"username": USERNAME, "password": PASSWORD}
    try:
        login_resp = session.post(LOGIN_URL, data=login_data, timeout=10)
        if login_resp.status_code != 200 or "login" in login_resp.url.lower():
            print(f"Login failed! Status: {login_resp.status_code}")
            print(login_resp.text)
            exit(1)
        print("Login successful. Starting crawl...")
    except Exception as e:
        print(f"Login request failed: {e}")
        exit(1)

    crawl(BASE_URL)
    print("\nBroken links found:")
    for url, reason in broken_links:
        print(f"{url} -> {reason}")
    print(f"\nChecked {len(visited)} pages, found {len(broken_links)} broken links.")

if __name__ == "__main__":
    print(f"Starting crawl at {BASE_URL}")
    crawl(BASE_URL)
    print("\nBroken links found:")
    for url, reason in broken_links:
        print(f"{url} -> {reason}")
    print(f"\nChecked {len(visited)} pages, found {len(broken_links)} broken links.")
