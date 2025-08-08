import re

def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r'[\s\t\n]+', '-', text)
    text = re.sub(r'[^\w\-]', '', text)
    return text
