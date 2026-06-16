import re
import unicodedata


def preprocess(text: str) -> str:
    text = text.strip().lower()
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"\s+", " ", text)
    return text
