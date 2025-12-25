from presidio_analyzer import Pattern, PatternRecognizer

# Example pattern for German ID Card (Personalausweis)
# Format: 9 alphanumeric characters (excluding vowels to avoid words) + 1 check digit
# Simplified regex for demonstration
german_id_pattern = Pattern(name="german_id_pattern", regex=r"\b[0-9LMNP-Z]{9}\d\b", score=0.5)

class GermanIDRecognizer(PatternRecognizer):
    def __init__(self, supported_language=None):
        super().__init__(
            supported_entity="DE_ID_CARD",
            patterns=[german_id_pattern],
            context=["id", "ausweis", "pass"],
            supported_language=supported_language
        )

# Spaced IBAN Pattern (Presidio sometimes struggles with spaces)
# Regex for DE IBAN with spaces: DE\d{2} \d{4} \d{4} \d{4} \d{4} \d{2}
# Updated to be more flexible with the last group (1-4 digits) to avoid truncation
spaced_iban_pattern = Pattern(name="spaced_iban_pattern", regex=r"\b[A-Z]{2}\d{2}(?: ?\d{4}){4,6}(?: ?\d{1,4})?\b", score=0.6)

class SpacedIBANRecognizer(PatternRecognizer):
    def __init__(self, supported_language=None):
        super().__init__(
            supported_entity="IBAN_CODE",
            patterns=[spaced_iban_pattern],
            context=["iban", "bank", "account"],
            name="SpacedIBANRecognizer",
            supported_language=supported_language
        )
