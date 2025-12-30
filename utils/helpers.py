# helpers.py - Utility Helper Functions

import re
import hashlib
from typing import Any, Dict, List, Optional
from datetime import datetime
import json
from logger import get_logger

logger = get_logger(__name__)

def generate_claim_id(patient_id: str, service_date: datetime) -> str:
    """
    Generate a unique claim ID based on patient ID and service date.
    """
    date_str = service_date.strftime("%Y%m%d")
    raw_id = f"{patient_id}_{date_str}_{datetime.utcnow().timestamp()}"
    
    # Create hash
    hash_obj = hashlib.md5(raw_id.encode())
    claim_id = f"CLM-{hash_obj.hexdigest()[:12].upper()}"
    
    logger.debug(f"Generated claim ID: {claim_id}")
    return claim_id

def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format amount as currency string.
    """
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£"
    }
    
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"

def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse date string in various formats.
    """
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%m-%d-%Y",
        "%d-%m-%Y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    logger.warning(f"Could not parse date: {date_str}")
    return None

def sanitize_text(text: str) -> str:
    """
    Sanitize text input by removing special characters.
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def validate_email(email: str) -> bool:
    """
    Validate email address format.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.
    """
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
    
    # Check if it's a valid length (10-15 digits)
    return bool(re.match(r'^\+?\d{10,15}$', cleaned))

def extract_codes(text: str, code_type: str = "ICD10") -> List[str]:
    """
    Extract medical codes from text.
    """
    codes = []
    
    if code_type == "ICD10":
        # ICD-10 format: Letter followed by 2-3 digits, optional decimal and more digits
        pattern = r'\b[A-Z]\d{2}(?:\.\d{1,4})?\b'
        codes = re.findall(pattern, text.upper())
    
    elif code_type == "CPT":
        # CPT format: 5 digits
        pattern = r'\b\d{5}\b'
        codes = re.findall(pattern, text)
    
    logger.debug(f"Extracted {len(codes)} {code_type} codes from text")
    return list(set(codes))  # Remove duplicates

def calculate_age(date_of_birth: datetime) -> int:
    """
    Calculate age from date of birth.
    """
    today = datetime.utcnow()
    age = today.year - date_of_birth.year
    
    # Adjust if birthday hasn't occurred this year
    if (today.month, today.day) < (date_of_birth.month, date_of_birth.day):
        age -= 1
    
    return age

def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """
    Deep merge two dictionaries.
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely load JSON string with fallback.
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"JSON decode error: {e}")
        return default

# Export
__all__ = [
    "generate_claim_id",
    "format_currency",
    "parse_date",
    "sanitize_text",
    "validate_email",
    "validate_phone",
    "extract_codes",
    "calculate_age",
    "merge_dicts",
    "safe_json_loads"
]
