"""
Rate limiting utility for API requests.
Implements token bucket algorithm for rate limiting.
"""

import time
import threading
from typing import Optional


class RateLimiter:
    """Rate limiter using token bucket algorithm."""
    
    def __init__(self, max_requests: int, time_window: int):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self.lock = threading.Lock()
    
    def wait_if_needed(self) -> None:
        """Wait if rate limit would be exceeded."""
        with self.lock:
            now = time.time()
            
            # Remove old requests outside the time window
            self.requests = [req_time for req_time in self.requests 
                            if now - req_time < self.time_window]
            
            # Check if we can make a request
            if len(self.requests) >= self.max_requests:
                # Calculate wait time
                oldest_request = min(self.requests)
                wait_time = self.time_window - (now - oldest_request)
                
                if wait_time > 0:
                    time.sleep(wait_time)
                    # Refresh after waiting
                    now = time.time()
                    self.requests = [req_time for req_time in self.requests 
                                   if now - req_time < self.time_window]
            
            # Record this request
            self.requests.append(now)
    
    def get_remaining_requests(self) -> int:
        """Get number of remaining requests in current window."""
        with self.lock:
            now = time.time()
            self.requests = [req_time for req_time in self.requests 
                           if now - req_time < self.time_window]
            return max(0, self.max_requests - len(self.requests))
    
    def get_reset_time(self) -> Optional[float]:
        """Get time when rate limit resets."""
        with self.lock:
            if not self.requests:
                return None
            oldest_request = min(self.requests)
            return oldest_request + self.time_window
