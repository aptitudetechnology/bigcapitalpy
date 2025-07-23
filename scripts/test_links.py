import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Configuration
BASE_URL = "http://simple.local:5000"  # Change to your running app's base URL
LOGIN_URL = BASE_URL + "/auth/login"     # Change to your login endpoint
USERNAME = "admin@bigcapitalpy.com"      # Change to your username
PASSWORD = "admin123"                    # Change to your password

# Global sets to keep track of visited URLs and broken links
visited = set()
broken_links = []

# Use a session to persist cookies (important for login)
session = requests.Session()

def is_internal(url):
    """Checks if a given URL is internal to the BASE_URL."""
    return url.startswith(BASE_URL) or url.startswith("/")

def crawl(url):
    """Recursively crawls internal links from a given URL."""
    full_url = urljoin(BASE_URL, url)

    # If the URL has already been visited or is external, skip it
    if full_url in visited or not is_internal(url):
        return

    visited.add(full_url)
    print(f"Crawling: {full_url}") # Added for better visibility during crawl

    try:
        resp = session.get(full_url, timeout=10) # Use the session for the request
        resp.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        broken_links.append((full_url, f"Request error: {e}"))
        return

    # Parse the HTML content to find all links
    soup = BeautifulSoup(resp.text, "html.parser")
    for link in soup.find_all("a", href=True):
        href = link["href"]
        # Ignore non-HTTP/HTTPS links
        if href.startswith("mailto:") or href.startswith("tel:") or href.startswith("javascript:"):
            continue

        next_url = urljoin(full_url, href)
        # Only crawl internal links (same domain as BASE_URL)
        if urlparse(next_url).netloc == urlparse(BASE_URL).netloc:
            crawl(next_url)

if __name__ == "__main__":
    print(f"Attempting to log in to {LOGIN_URL}...")

    # 1. Get the login page to extract the CSRF token
    try:
        login_page_resp = session.get(LOGIN_URL, timeout=10)
        login_page_resp.raise_for_status()
        soup = BeautifulSoup(login_page_resp.text, "html.parser")
        
        # Find the CSRF token (common names: csrf_token, _csrf, etc.)
        # This assumes the token is in a hidden input field named 'csrf_token'
        csrf_token_tag = soup.find("input", {"name": "csrf_token"})
        if not csrf_token_tag:
            print("Error: CSRF token not found on the login page. Check the HTML structure.")
            exit(1)
        csrf_token = csrf_token_tag["value"]
        print(f"CSRF token obtained: {csrf_token[:10]}...") # Print first 10 chars for brevity

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch login page: {e}")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while parsing login page: {e}")
        exit(1)

    # 2. Prepare login data including the CSRF token
    login_data = {
        "username": USERNAME,
        "password": PASSWORD,
        "csrf_token": csrf_token # Include the extracted CSRF token
    }

    # 3. Perform the login POST request
    try:
        login_resp = session.post(LOGIN_URL, data=login_data, timeout=10)
        login_resp.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        # Check if login was successful by looking for a redirect or specific text
        # Adjust this check based on your application's post-login behavior
        if "login" in login_resp.url.lower(): # If still on a login-related URL, it failed
            print(f"Login failed! Status: {login_resp.status_code}")
            print("Response content (might indicate reason):")
            print(login_resp.text)
            exit(1)
        
        print("Login successful. Starting crawl...")
    except requests.exceptions.RequestException as e:
        print(f"Login POST request failed: {e}")
        print("Response content (if available):")
        if hasattr(e, 'response') and e.response is not None:
            print(e.response.text)
        exit(1)

    # 4. Start crawling from the base URL after successful login
    crawl(BASE_URL)

    print("\n--- Crawl Results ---")
    print("\nBroken links found:")
    if broken_links:
        for url, reason in broken_links:
            print(f"{url} -> {reason}")
    else:
        print("No broken links found!")
        
    print(f"\nSummary: Checked {len(visited)} pages, found {len(broken_links)} broken links.")
