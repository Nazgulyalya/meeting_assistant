import re

def scrub_pii(text: str) -> str:
    """Remove common PII before storing in vector DB."""
    # Emails
    text = re.sub(r'\b[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}\b', '[EMAIL]', text)
    # Phone numbers
    text = re.sub(r'\b(\+?\d[\d\s\-().]{7,})\b', '[PHONE]', text)
    # Credit cards (basic)
    text = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CARD]', text)
    return text