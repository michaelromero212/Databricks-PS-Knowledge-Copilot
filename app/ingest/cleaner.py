import re

class Cleaner:
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Replaces multiple whitespace characters with a single space."""
        return re.sub(r'\s+', ' ', text).strip()

    @staticmethod
    def clean_text(text: str) -> str:
        """Performs a series of cleaning steps on the text."""
        text = Cleaner.normalize_whitespace(text)
        # Add more cleaning steps here if needed (e.g., removing special chars)
        return text
