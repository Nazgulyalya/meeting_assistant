import re

def scrub_pii(text: str) -> str:
    """Remove PII before storing in vector DB."""
    # Emails
    text = re.sub(r'\b[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}\b', '[EMAIL]', text)
    # Phone numbers
    text = re.sub(r'\b(\+?\d[\d\s\-().]{7,})\b', '[PHONE]', text)
    # Credit cards
    text = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CARD]', text)
    # SSN (US format)
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
    # IP addresses
    text = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP]', text)
    # URLs
    text = re.sub(r'https?://[\w\-./]+', '[URL]', text)
    return text


def detect_pii(text: str) -> dict:
    """Detect which types of PII are present (without modifying text)."""
    found = {}
    patterns = {
        "emails": r'\b[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}\b',
        "phones": r'\b\+?\d[\d\s\-().]{7,}\b',
        "credit_cards": r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "ip_addresses": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
    }
    for name, pattern in patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            found[name] = len(matches)
    return found