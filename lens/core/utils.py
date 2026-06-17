import requests
import time
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# Simple rate limiter to avoid 429s
LAST_REQUEST_TIME = 0
MIN_INTERVAL = 2  # Minimum seconds between requests

def get_with_retry(url: str, params=None, headers=None, timeout=20):
    global LAST_REQUEST_TIME
    
    # Simple rate limiting
    elapsed = time.time() - LAST_REQUEST_TIME
    if elapsed < MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - elapsed)
        
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=2,  # Reduced retries for faster failure
        backoff_factor=1,  # Faster backoff
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    response = session.get(url, params=params, headers=headers, timeout=timeout)
    LAST_REQUEST_TIME = time.time()
    return response
