import re

def scrub_pii(text: str) -> str:
    """Remove PII before storing in vector DB — regex + NER."""
    # Regex layer
    text = re.sub(r'\b[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}\b', '[EMAIL]', text)
    text = re.sub(r'\b(\+?\d[\d\s\-().]{7,})\b', '[PHONE]', text)
    text = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CARD]', text)
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
    text = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP]', text)
    text = re.sub(r'https?://[\w\-./]+', '[URL]', text)

    # NER layer (spaCy) — names, locations, organizations
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        ents = sorted(doc.ents, key=lambda e: -e.start_char)
        for ent in ents:
            if ent.label_ in ("PERSON", "GPE", "ORG"):
                placeholder = f"[{ent.label_}]"
                text = text[:ent.start_char] + placeholder + text[ent.end_char:]
    except Exception:
        pass

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