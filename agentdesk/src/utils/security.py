import re

class PIIMasker:
    """Enterprise-grade PII masking utility"""
    
    EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_REGEX = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    
    @staticmethod
    def mask(text: str) -> str:
        if not text:
            return ""
        text = re.sub(PIIMasker.EMAIL_REGEX, '[EMAIL_REDACTED]', text)
        text = re.sub(PIIMasker.PHONE_REGEX, '[PHONE_REDACTED]', text)
        return text
