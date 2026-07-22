import re

URL_PATTERN = re.compile(r'https?://\S+|www\.\S+|\S+\.\S+')

def contains_links(text: str) -> bool:
    return bool(URL_PATTERN.search(text))

def contains_bad_words(text: str, bad_words_str: str) -> bool:
    if not bad_words_str:
        return False
    bad_words = [w.strip().lower() for w in bad_words_str.split(",") if w.strip()]
    text_lower = text.lower()
    return any(word in text_lower for word in bad_words)