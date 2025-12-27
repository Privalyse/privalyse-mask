import dateparser
import hashlib
from typing import Optional

def parse_and_format_date(date_string: str) -> str:
    """
    Parses a date string and returns a generalized format {Date_Month_Year}.
    
    Args:
        date_string: A date string in various formats (e.g., "12.10.2000", "October 5th, 2025").
        
    Returns:
        A semantic placeholder like "{Date_October_2000}" or "{Date_General}" if parsing fails.
    """
    try:
        # Prefer DMY order for European dates as requested
        dt = dateparser.parse(date_string, settings={'DATE_ORDER': 'DMY'})
        if dt:
            return f"{{Date_{dt.strftime('%B_%Y')}}}"
    except (ValueError, TypeError, AttributeError) as e:
        # ValueError: invalid date format
        # TypeError: None passed to parse
        # AttributeError: unexpected return type from dateparser
        pass
    return "{Date_General}"

def generate_hash_suffix(text: str, length: int = 5, salt: str = "") -> str:
    """
    Generates a short, deterministic hash suffix for consistent pseudonymization.
    
    Uses MD5 for speed (not for cryptographic security). The same input text
    and salt will always produce the same hash, enabling consistent masking
    across multiple calls.
    
    Args:
        text: The text to hash (e.g., a person's name).
        length: Number of hex characters to return (default: 5).
        salt: Optional salt to vary hashes per project/session.
        
    Returns:
        A lowercase hex string of the specified length.
    """
    data = f"{text}{salt}".encode()
    hash_object = hashlib.md5(data)
    return hash_object.hexdigest()[:length]
