"""
Custom PII recognizers for Presidio.

This module extends Presidio's built-in entity recognition with patterns
for specific document types that are not well-covered by default recognizers.
"""

from typing import List, Optional
from presidio_analyzer import Pattern, PatternRecognizer


# =============================================================================
# German ID Card (Personalausweis) Recognizer
# =============================================================================

# German ID card format:
# - 9 alphanumeric characters (0-9, L-Z excluding vowels A, E, I, O, U)
# - 1 check digit (0-9)
# - Example: T220001293
# Reference: https://de.wikipedia.org/wiki/Personalausweis_(Deutschland)
GERMAN_ID_PATTERN = Pattern(
    name="german_id_pattern",
    regex=r"\b[0-9LMNP-Z]{9}\d\b",
    score=0.5  # Lower confidence; needs context boost
)


class GermanIDRecognizer(PatternRecognizer):
    """
    Recognizes German national ID card (Personalausweis) numbers.
    
    The pattern matches the standard format of 10 characters:
    9 alphanumeric (excluding vowels) + 1 check digit.
    
    Context words like "Ausweis", "ID", "Pass" boost the confidence score.
    """
    
    def __init__(self, supported_language: Optional[str] = None) -> None:
        super().__init__(
            supported_entity="DE_ID_CARD",
            patterns=[GERMAN_ID_PATTERN],
            context=["id", "ausweis", "pass", "personalausweis", "identity"],
            supported_language=supported_language
        )


# =============================================================================
# Spaced IBAN Recognizer
# =============================================================================

# IBAN format with optional spaces (Presidio's default struggles with spaces):
# - 2 letter country code + 2 check digits + up to 30 alphanumeric chars
# - Common formats: DE89 3704 0044 0532 0130 00 (with spaces)
# - This regex handles 4-digit groups with optional spacing
SPACED_IBAN_PATTERN = Pattern(
    name="spaced_iban_pattern",
    regex=r"\b[A-Z]{2}\d{2}(?: ?\d{4}){4,6}(?: ?\d{1,4})?\b",
    score=0.6  # Medium confidence; IBAN format is fairly unique
)


class SpacedIBANRecognizer(PatternRecognizer):
    """
    Recognizes International Bank Account Numbers (IBANs) with optional spacing.
    
    Presidio's built-in IBAN recognizer sometimes misses IBANs formatted with
    spaces between digit groups (e.g., "DE89 3704 0044 0532 0130 00").
    This recognizer handles both spaced and non-spaced formats.
    
    Context words like "IBAN", "bank", "account" boost the confidence score.
    """
    
    def __init__(self, supported_language: Optional[str] = None) -> None:
        super().__init__(
            supported_entity="IBAN_CODE",
            patterns=[SPACED_IBAN_PATTERN],
            context=["iban", "bank", "account", "konto", "bankverbindung"],
            name="SpacedIBANRecognizer",
            supported_language=supported_language
        )
