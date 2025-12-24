import dateparser
import hashlib

def parse_and_format_date(date_string: str) -> str:
    """
    Parses a date string and returns a generalized format {Date_Month_Year}.
    Returns {Date_General} if parsing fails.
    """
    try:
        # Prefer DMY order for European dates as requested
        dt = dateparser.parse(date_string, settings={'DATE_ORDER': 'DMY'})
        if dt:
            return f"{{Date_{dt.strftime('%B_%Y')}}}"
    except:
        pass
    return "{Date_General}"

def generate_hash_suffix(text: str, length: int = 5, salt: str = "") -> str:
    """Generates a short hash suffix for a given text to ensure consistency."""
    data = f"{text}{salt}".encode()
    hash_object = hashlib.md5(data)
    return hash_object.hexdigest()[:length]
