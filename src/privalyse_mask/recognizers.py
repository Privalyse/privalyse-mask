from presidio_analyzer import Pattern, PatternRecognizer

# Example pattern for German ID Card (Personalausweis)
# Format: 9 alphanumeric characters (excluding vowels to avoid words) + 1 check digit
# Simplified regex for demonstration
german_id_pattern = Pattern(name="german_id_pattern", regex=r"\b[0-9LMNP-Z]{9}\d\b", score=0.5)

class GermanIDRecognizer(PatternRecognizer):
    def __init__(self, supported_language: str = "en"):
        super().__init__(
            supported_entity="DE_ID_CARD",
            patterns=[german_id_pattern],
            context=["id", "ausweis", "pass"],
            supported_language=supported_language
        )

# Spaced IBAN Pattern (Presidio sometimes struggles with spaces)
# Regex for DE IBAN with spaces: DE\d{2} \d{4} \d{4} \d{4} \d{4} \d{2}
spaced_iban_pattern = Pattern(name="spaced_iban_pattern", regex=r"\b[A-Z]{2}\d{2}(?: ?\d{4}){4,6}\b", score=0.6)

class SpacedIBANRecognizer(PatternRecognizer):
    def __init__(self, supported_language: str = "en"):
        super().__init__(
            supported_entity="IBAN",
            patterns=[spaced_iban_pattern],
            context=["iban", "bank", "account"],
            supported_language=supported_language
        )

# 1. Strict Street Pattern (Must contain a known suffix/type)
# Matches: "Hauptstr. 10", "Musterstraße 42", "Alexanderplatz 1"
# Suffixes: straße, str., platz, weg, gasse, allee, damm, ring, hof, markt, wall, street, st., road, rd., avenue, ave.
# Wrapped in (?-i:...) to enforce case sensitivity
strict_street_regex = r"(?-i:\b[A-ZÄÖÜ][a-zäöüß\.]*(?:straße|str\.|platz|weg|gasse|allee|damm|ring|hof|markt|wall|Street|St\.|Road|Rd\.|Avenue|Ave\.)(?:[ -](?:[A-ZÄÖÜ][a-zäöüß]+|den|der|die|am|im|in|auf|dem))* \d+[a-zA-Z]?\b)"
strict_street_pattern = Pattern(name="strict_street_pattern", regex=strict_street_regex, score=0.85)

# 2. City Prefix Pattern (City, Street Number)
# Matches: "Berlin, Alexanderplatz 1", "Frankfurt am Main, Zeil 10"
# Allows multi-word cities (e.g. Frankfurt am Main)
# FIX: City parts must be Capitalized (except particles) to avoid matching "Send it to Hamburg"
# Wrapped in (?-i:...) to enforce case sensitivity
city_prefix_regex = r"(?-i:\b[A-ZÄÖÜ][a-zäöüß]+(?:[ -](?:[A-ZÄÖÜ][a-zäöüß]+|am|an|der|auf|dem))*, [A-ZÄÖÜ][a-zäöüß\.]+(?:[ -](?:[A-ZÄÖÜ][a-zäöüß]+|den|der|die|am|im|in|auf|dem))* \d+[a-zA-Z]?\b)"
city_prefix_pattern = Pattern(name="city_prefix_pattern", regex=city_prefix_regex, score=0.9)

# 3. City Suffix Pattern (Street Number, Zip City OR Street Number, City)
# Matches: "Musterstraße 42, Munich", "Schlossallee 1, 12345 Entenhausen"
# Wrapped in (?-i:...) to enforce case sensitivity
# FIX: Enforce Capitalization for street parts to avoid matching verbs like "wohnt"
city_suffix_regex = r"(?-i:\b[A-ZÄÖÜ][a-zäöüß\.]+(?:[ -](?:[A-ZÄÖÜ][a-zäöüß]+|den|der|die|am|im|in|auf|dem))* \d+[a-zA-Z]?, (?:(?:\d{5} )?[A-ZÄÖÜ][a-zäöüß]+)\b)"
city_suffix_pattern = Pattern(name="city_suffix_pattern", regex=city_suffix_regex, score=0.9)

class GermanAddressRecognizer(PatternRecognizer):
    def __init__(self, supported_language: str = "en"):
        super().__init__(
            supported_entity="ADDRESS",
            patterns=[strict_street_pattern, city_prefix_pattern, city_suffix_pattern],
            context=["straße", "str.", "platz", "weg", "gasse", "allee", "live in", "wohne in", "address", "at", "in"],
            supported_language=supported_language
        )

# International Address Pattern (Number Street) - US/UK Style
# Matches: "123 Main St", "10 Downing Street"
# Must have a known street suffix to avoid false positives like "5 Apples"
intl_street_regex = r"(?-i:\b\d+ [A-ZÄÖÜ][a-zäöüß]+(?:[ -](?:[A-ZÄÖÜa-zäöüß]+|de|du|des|la|le|the|of))* (?:Street|St\.?|Road|Rd\.?|Avenue|Ave\.?|Way|Lane|Dr\.?|Drive|Boulevard|Blvd\.?|Place|Pl\.?|Square|Sq\.?)(?:, [A-ZÄÖÜ][a-zäöüß]+(?:[ -][A-ZÄÖÜa-zäöüß]+)*)?\b)"
intl_street_pattern = Pattern(name="intl_street_pattern", regex=intl_street_regex, score=0.85)

# French Address Pattern (Number Type Name)
# Matches: "10 Rue de la Paix", "10 Avenue des Champs-Élysées"
french_street_regex = r"(?-i:\b\d+(?: (?:bis|ter))? (?:Rue|Avenue|Ave\.?|Boulevard|Blvd\.?|Allée|Place|Impasse|Cours|Quai|Passage|Route|Chemin)(?: [dD][eu'](?:s| la)?| [lL][ae]| [dD]es)? [A-ZÄÖÜ][a-zäöüß]+(?:[ -](?:[A-ZÄÖÜa-zäöüß]+|de|du|des|la|le|d'))*(?:, [A-ZÄÖÜ][a-zäöüß]+)?\b)"
french_street_pattern = Pattern(name="french_street_pattern", regex=french_street_regex, score=0.85)

class InternationalAddressRecognizer(PatternRecognizer):
    def __init__(self, supported_language: str = "en"):
        super().__init__(
            supported_entity="ADDRESS",
            patterns=[intl_street_pattern, french_street_pattern],
            context=["live at", "visit", "address", "rue", "street", "avenue", "habite", "au"],
            supported_language=supported_language
        )
