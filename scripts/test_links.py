import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

# Configuration
BASE_URL = "http://simple.local:5000"  # Change to your running app's base URL
LOGIN_URL = BASE_URL + "/auth/login"     # Change to your login endpoint
USERNAME = "admin@bigcapitalpy.com"      # Change to your username
PASSWORD = "admin123"                    # Change to your password

# Global sets to keep track of visited URLs and issues found
visited = set()
broken_links = []
dummy_links = []
mismatch_links = []
rendering_errors = []  # New category for template/rendering errors

# Use a session to persist cookies (important for login)
session = requests.Session()

def is_internal(url):
    """Checks if a given URL is internal to the BASE_URL."""
    return url.startswith(BASE_URL) or url.startswith("/")

def extract_error_details(response_text, status_code):
    """Extract detailed error information from error pages."""
    error_info = {
        'type': 'Unknown Error',
        'message': '',
        'details': ''
    }
    
    # Try to parse as HTML first
    try:
        soup = BeautifulSoup(response_text, "html.parser")
        
        # Look for common error patterns in HTML
        # Check for Flask/Werkzeug debug pages
        werkzeug_title = soup.find('title')
        if werkzeug_title and 'werkzeug debugger' in werkzeug_title.get_text().lower():
            error_info['type'] = 'Werkzeug Debug Error'
            
            # Extract the main error message
            error_summary = soup.find('div', class_='summary')
            if error_summary:
                error_info['message'] = error_summary.get_text(strip=True)
        
        # Check for Jinja2 errors specifically
        if 'jinja2.exceptions' in response_text.lower():
            error_info['type'] = 'Jinja2 Template Error'
            
            # Extract Jinja2 error details using regex
            jinja_match = re.search(r'jinja2\.exceptions\.(\w+)Error:\s*(.+?)(?:\n|$)', response_text, re.IGNORECASE)
            if jinja_match:
                error_info['message'] = f"{jinja_match.group(1)}Error: {jinja_match.group(2).strip()}"
        
        # Check for other Python exceptions
        python_exception_match = re.search(r'(\w+Error):\s*(.+?)(?:\n|<br|$)', response_text)
        if python_exception_match and error_info['type'] == 'Unknown Error':
            error_info['type'] = 'Python Exception'
            error_info['message'] = f"{python_exception_match.group(1)}: {python_exception_match.group(2).strip()}"
        
        # Look for generic error messages in common HTML structures
        if not error_info['message']:
            # Check for common error message containers
            error_containers = soup.find_all(['div', 'p', 'span'], 
                                           class_=lambda x: x and any(keyword in x.lower() for keyword in ['error', 'exception', 'traceback']))
            
            for container in error_containers:
                text = container.get_text(strip=True)
                if text and len(text) > 10:  # Avoid empty or too-short messages
                    error_info['message'] = text[:200] + ('...' if len(text) > 200 else '')
                    break
    
    except Exception as e:
        # If HTML parsing fails, try to extract error info from raw text
        pass
    
    # Fallback: look for error patterns in raw text
    if not error_info['message']:
        # Common error patterns
        error_patterns = [
            (r'jinja2\.exceptions\.(\w+):\s*(.+?)(?:\n|$)', 'Jinja2 Error'),
            (r'(\w+Error):\s*(.+?)(?:\n|$)', 'Python Exception'),
            (r'Internal Server Error', 'Internal Server Error'),
            (r'Template not found:\s*(.+?)(?:\n|$)', 'Template Missing'),
            (r'NameError:\s*(.+?)(?:\n|$)', 'Name Error'),
            (r'AttributeError:\s*(.+?)(?:\n|$)', 'Attribute Error'),
        ]
        
        for pattern, error_type in error_patterns:
            match = re.search(pattern, response_text, re.IGNORECASE | re.MULTILINE)
            if match:
                error_info['type'] = error_type
                if len(match.groups()) > 1:
                    error_info['message'] = f"{match.group(1)}: {match.group(2).strip()}"
                else:
                    error_info['message'] = match.group(1).strip() if match.group(1) else match.group(0)
                break
    
    # If still no message, provide a generic one based on status code
    if not error_info['message']:
        if status_code == 500:
            error_info['message'] = 'Internal Server Error (no details available)'
        elif status_code == 502:
            error_info['message'] = 'Bad Gateway'
        elif status_code == 503:
            error_info['message'] = 'Service Unavailable'
        else:
            error_info['message'] = f'HTTP {status_code} Error'
    
    return error_info

def is_dummy_link(href, link_element, soup):
    """Check if a link is a dummy/placeholder link."""
    if not href:
        return True, "Empty href"
    
    href = href.strip()
    
    # First check if this is a functional dropdown/menu toggle
    if href == "#" or href.startswith("#"):
        # Check for dropdown/menu functionality indicators
        classes = link_element.get('class', [])
        if isinstance(classes, str):
            classes = classes.split()
        
        # Look for dropdown/toggle classes
        dropdown_classes = {'dropdown-toggle', 'menu-toggle', 'submenu-toggle', 'toggle', 'accordion-toggle'}
        if any(cls in dropdown_classes for cls in classes):
            # Check if it has dropdown children or data attributes
            data_attrs = [attr for attr in link_element.attrs.keys() if attr.startswith('data-')]
            if data_attrs:
                return False, None  # This is a functional dropdown trigger
        
        # Check if this link has dropdown children in the DOM
        parent = link_element.parent
        if parent:
            # Look for dropdown content siblings or children
            dropdown_indicators = parent.find_all(class_=lambda x: x and any(
                keyword in str(x).lower() for keyword in ['dropdown-content', 'dropdown-menu', 'submenu-content', 'menu-content']
            ))
            if dropdown_indicators:
                return False, None  # This is a functional dropdown with children
            
            # Also check for immediate siblings with dropdown-link class
            siblings = parent.find_all('a', class_=lambda x: x and 'dropdown-link' in str(x))
            if siblings and len(siblings) > 0:
                return False, None  # This appears to be a dropdown parent
    
    # Now check for actual dummy/placeholder patterns
    dummy_patterns = [
        (r"^#$", "Hash-only link (no dropdown functionality)"),
        (r"^javascript:void\(0\)$", "JavaScript void placeholder"),
        (r"^javascript:;$", "JavaScript semicolon placeholder"),
        (r"^javascript:$", "Empty JavaScript"),
        (r"^$", "Empty href"),
        (r"^/todo$", "TODO placeholder"),
        (r"^/placeholder$", "Placeholder URL"),
        (r"^/undefined$", "Undefined URL"),
        (r"^#(?!$).+$", "Fragment-only link")  # Fragment links like #section but not just #
    ]
    
    for pattern, description in dummy_patterns:
        if re.match(pattern, href, re.IGNORECASE):
            return True, description
    
    return False, None

def extract_link_keywords(text):
    """Extract meaningful keywords from link text."""
    if not text:
        return set()
    
    # Clean and normalize text
    text = re.sub(r'[^\w\s]', ' ', text.lower().strip())
    words = text.split()
    
    # Remove common words that don't indicate purpose
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', '&'}
    keywords = {word for word in words if word not in stop_words and len(word) > 2}
    
    return keywords

def extract_url_keywords(url):
    """Extract meaningful keywords from URL path."""
    if not url:
        return set()
    
    try:
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # Split path and remove empty parts
        path_parts = [part for part in path.split('/') if part]
        
        # Extract keywords from path parts
        keywords = set()
        for part in path_parts:
            # Split on common separators
            words = re.split(r'[-_]', part)
            keywords.update(word for word in words if len(word) > 2)
        
        return keywords
    except:
        return set()

def check_text_url_mismatch(link_text, href, full_url):
    """Check if link text and URL destination seem mismatched."""
    if not link_text or not href:
        return False, None
    
    text_keywords = extract_link_keywords(link_text)
    url_keywords = extract_url_keywords(full_url)
    
    if not text_keywords or not url_keywords:
        return False, None
    
    # Define common action/page mappings
    keyword_mappings = {
        # Actions
        'login': {'login', 'signin', 'auth'},
        'logout': {'logout', 'signout', 'auth'},
        'register': {'register', 'signup', 'auth'},
        'create': {'create', 'new', 'add'},
        'edit': {'edit', 'update', 'modify'},
        'delete': {'delete', 'remove', 'destroy'},
        'view': {'view', 'show', 'display', 'details'},
        'list': {'list', 'index', 'all'},
        'save': {'save', 'update', 'store'},
        'cancel': {'cancel', 'back', 'return'},
        
        # Pages/Sections
        'dashboard': {'dashboard', 'home', 'main'},
        'users': {'users', 'user', 'people', 'accounts'},
        'products': {'products', 'product', 'items', 'inventory'},
        'orders': {'orders', 'order', 'purchases'},
        'invoices': {'invoices', 'invoice', 'bills'},
        'reports': {'reports', 'report', 'analytics'},
        'settings': {'settings', 'config', 'preferences'},
        'organization': {'organization', 'org', 'company'},
        'permissions': {'permissions', 'roles', 'access'},
        'backup': {'backup', 'restore', 'export', 'import'},
        'sales': {'sales', 'sell', 'revenue'},
        'accounting': {'accounting', 'finance', 'books'},
        'inventory': {'inventory', 'stock', 'items'},
        'system': {'system', 'admin', 'config'}
    }
    
    # Check for direct contradictions
    for text_word in text_keywords:
        if text_word in keyword_mappings:
            expected_keywords = keyword_mappings[text_word]
            if not any(keyword in url_keywords for keyword in expected_keywords):
                # Check if URL suggests a completely different action/page
                for url_word in url_keywords:
                    if url_word in keyword_mappings:
                        url_expected = keyword_mappings[url_word]
                        if not any(keyword in text_keywords for keyword in url_expected):
                            return True, f"Text suggests '{text_word}' but URL suggests '{url_word}'"
    
    # Check for action mismatches (more specific)
    action_words_text = text_keywords & {'create', 'edit', 'delete', 'view', 'save', 'cancel', 'login', 'logout'}
    action_words_url = url_keywords & {'create', 'edit', 'delete', 'view', 'save', 'cancel', 'login', 'logout', 'new', 'update', 'destroy', 'show'}
    
    if action_words_text and action_words_url:
        # Direct action contradiction
        if not action_words_text & action_words_url:
            return True, f"Action mismatch: text has '{', '.join(action_words_text)}' but URL has '{', '.join(action_words_url)}'"
    
    return False, None

def crawl(url):
    """Recursively crawls internal links from a given URL."""
    full_url = urljoin(BASE_URL, url)

    # If the URL has already been visited or is external, skip it
    if full_url in visited or not is_internal(url):
        return

    visited.add(full_url)
    print(f"Crawling: {full_url}")

    try:
        resp = session.get(full_url, timeout=10)
        
        # Check for server errors (5xx) which might be rendering errors
        if 500 <= resp.status_code < 600:
            error_details = extract_error_details(resp.text, resp.status_code)
            rendering_errors.append((full_url, resp.status_code, error_details))
            print(f"  ⚠️  Rendering error detected: {error_details['type']}")
            return  # Don't try to parse links from error pages
        
        # Raise for other HTTP errors (4xx, etc.)
        resp.raise_for_status()
        
    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors that aren't 5xx (like 404, 403, etc.)
        if hasattr(e, 'response') and e.response is not None:
            if 500 <= e.response.status_code < 600:
                # This should have been caught above, but just in case
                error_details = extract_error_details(e.response.text, e.response.status_code)
                rendering_errors.append((full_url, e.response.status_code, error_details))
            else:
                broken_links.append((full_url, f"HTTP {e.response.status_code}: {str(e)}"))
        else:
            broken_links.append((full_url, f"HTTP error: {str(e)}"))
        return
        
    except requests.exceptions.RequestException as e:
        broken_links.append((full_url, f"Request error: {e}"))
        return

    # Parse the HTML content to find all links
    try:
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        rendering_errors.append((full_url, 200, {
            'type': 'HTML Parsing Error',
            'message': f'Could not parse HTML: {str(e)}',
            'details': ''
        }))
        return
    
    for link in soup.find_all("a", href=True):
        href = link["href"]
        link_text = link.get_text(strip=True)
        
        # Check for dummy/placeholder links
        is_dummy, dummy_reason = is_dummy_link(href, link, soup)
        if is_dummy:
            dummy_links.append((full_url, href, link_text, dummy_reason))
            continue  # Skip further processing for dummy links
        
        # Ignore non-HTTP/HTTPS links for crawling but still check for issues
        if href.startswith("mailto:") or href.startswith("tel:"):
            continue

        next_url = urljoin(full_url, href)
        
        # Check for text/URL mismatches on internal links
        if urlparse(next_url).netloc == urlparse(BASE_URL).netloc:
            is_mismatch, mismatch_reason = check_text_url_mismatch(link_text, href, next_url)
            if is_mismatch:
                mismatch_links.append((full_url, next_url, link_text, mismatch_reason))
            
            # Continue crawling internal links
            crawl(next_url)

if __name__ == "__main__":
    print(f"Attempting to log in to {LOGIN_URL}...")
    print(f"Using Email: {USERNAME}")
    print(f"Using Password: {PASSWORD}")

    # 1. Get the login page to extract the CSRF token
    try:
        login_page_resp = session.get(LOGIN_URL, timeout=10)
        login_page_resp.raise_for_status()
        soup = BeautifulSoup(login_page_resp.text, "html.parser")
        
        # Find the CSRF token
        csrf_token_tag = soup.find("input", {"name": "csrf_token"})
        if not csrf_token_tag:
            print("Error: CSRF token not found on the login page. Check the HTML structure.")
            exit(1)
        csrf_token = csrf_token_tag["value"]
        print(f"CSRF token obtained: {csrf_token[:10]}...")

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch login page: {e}")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while parsing login page: {e}")
        exit(1)

    # 2. Prepare login data including the CSRF token
    login_data = {
        "email": USERNAME,
        "password": PASSWORD,
        "csrf_token": csrf_token
    }

    # 3. Perform the login POST request
    try:
        login_resp = session.post(LOGIN_URL, data=login_data, timeout=10)
        login_resp.raise_for_status()

        print(f"Login POST request completed. Final URL: {login_resp.url}")

        # Check if login was successful
        if "login" in login_resp.url.lower() or login_resp.url == LOGIN_URL:
            print(f"Login failed! Status: {login_resp.status_code}")
            print("--- BEGIN RESPONSE CONTENT ---")
            print(login_resp.text)
            print("--- END RESPONSE CONTENT ---")
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

    print("\n" + "="*60)
    print("CRAWL RESULTS")
    print("="*60)
    
    print(f"\nSummary: Checked {len(visited)} pages")
    print(f"Found {len(broken_links)} broken links")
    print(f"Found {len(dummy_links)} dummy/placeholder links") 
    print(f"Found {len(mismatch_links)} text/URL mismatches")
    print(f"Found {len(rendering_errors)} rendering/template errors")

    if rendering_errors:
        print(f"\n--- RENDERING/TEMPLATE ERRORS ({len(rendering_errors)}) ---")
        for url, status_code, error_info in rendering_errors:
            print(f"🔥 {url}")
            print(f"   Status: HTTP {status_code}")
            print(f"   Type: {error_info['type']}")
            print(f"   Error: {error_info['message']}")
            if error_info['details']:
                print(f"   Details: {error_info['details']}")
            print()

    if broken_links:
        print(f"\n--- BROKEN LINKS ({len(broken_links)}) ---")
        for url, reason in broken_links:
            print(f"❌ {url}")
            print(f"   Reason: {reason}\n")
    
    if dummy_links:
        print(f"\n--- DUMMY/PLACEHOLDER LINKS ({len(dummy_links)}) ---")
        for page_url, href, link_text, reason in dummy_links:
            print(f"🔗 Page: {page_url}")
            print(f"   Link: '{link_text}' -> {href}")
            print(f"   Issue: {reason}\n")
    
    if mismatch_links:
        print(f"\n--- TEXT/URL MISMATCHES ({len(mismatch_links)}) ---")
        for page_url, link_url, link_text, reason in mismatch_links:
            print(f"⚠️  Page: {page_url}")
            print(f"   Link: '{link_text}' -> {link_url}")
            print(f"   Issue: {reason}\n")
    
    if not broken_links and not dummy_links and not mismatch_links and not rendering_errors:
        print("\n🎉 No issues found! All links appear to be working correctly.")