from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import logging
import re
import phonenumbers
from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_analyzer.nlp_engine import NlpEngineProvider
from .utils import parse_and_format_date, generate_hash_suffix
from .recognizers import GermanIDRecognizer, SpacedIBANRecognizer

logger = logging.getLogger(__name__)

# Common false positives for NER (German & English)
STOP_WORDS = {
    # German
    "ich", "du", "er", "sie", "es", "wir", "ihr", "sie", "mein", "dein", "sein", "ihr", "unser", "euer", "ihr", "der", "die", "das",
    # English
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves"
}

class PrivalyseMasker:
    def __init__(self, languages: List[str] = ["en", "de"], allow_list: List[str] = [], seed: str = "", model_size: str = "lg"):
        """
        Initialize the PrivalyseMasker.
        :param languages: List of languages for Presidio (e.g. ["en", "de"])
        :param allow_list: List of terms that should NEVER be masked (e.g. Company names)
        :param seed: Optional salt string to randomize hashes per project/session.
        :param model_size: Spacy model size to use ("sm", "md", "lg"). Default is "lg".
        """
        self.allow_list = set(word.lower() for word in allow_list)
        self.allow_list.update(STOP_WORDS)
        self.seed = seed
        
        try:
            # Configure NLP Engine
            nlp_configuration = {
                "nlp_engine_name": "spacy",
                "models": []
            }
            
            for lang in languages:
                # English uses 'web', others (de, fr, es, it) usually use 'news'
                model_type = "web" if lang == "en" else "news"
                model_name = f"{lang}_core_{model_type}_{model_size}"
                nlp_configuration["models"].append({"lang_code": lang, "model_name": model_name})

            provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
            nlp_engine = provider.create_engine()
            
            self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=languages)
            # Add custom recognizers
            
            for lang in languages:
                self.analyzer.registry.add_recognizer(GermanIDRecognizer(supported_language=lang))
                self.analyzer.registry.add_recognizer(SpacedIBANRecognizer(supported_language=lang))
            
        except OSError as e:
            # OSError is raised when spacy model is not found
            logger.warning(f"Failed to load spacy model: {e}")
            logger.warning("Run: python -m spacy download <model_name>")
            self.analyzer = None
        except ImportError as e:
            # ImportError when presidio or spacy not installed
            logger.warning(f"Missing dependency: {e}")
            logger.warning("Run: pip install presidio-analyzer spacy")
            self.analyzer = None
        except (ValueError, RuntimeError) as e:
            # ValueError: invalid configuration
            # RuntimeError: other initialization failures
            logger.warning(f"Failed to initialize AnalyzerEngine: {e}")
            self.analyzer = None

    def mask(self, text: str, language: str = "en") -> Tuple[str, Dict[str, str]]:
        """
        Masks PII in the text and returns the masked text and a mapping to restore it.
        """
        if not self.analyzer:
            raise RuntimeError("Analyzer not initialized.")

        # Analyze text
        results = self.analyzer.analyze(text=text, language=language)
        
        # Filter overlaps (simple greedy strategy: keep first/longest)
        # Presidio results are not guaranteed to be non-overlapping
        results = self._remove_overlaps(results)
        
        # Merge adjacent dates (e.g. "October 5th, 2025" -> "October 5th" + "2025")
        results = self._merge_adjacent_dates(text, results)
        
        # Sort by start index descending to replace from end
        results.sort(key=lambda x: x.start, reverse=True)
        
        masked_text = text
        mapping = {}
        
        for result in results:
            entity_text = text[result.start:result.end]
            
            # Check allow list
            if entity_text.lower() in self.allow_list:
                continue

            entity_type = result.entity_type
            
            surrogate = self._generate_surrogate(entity_type, entity_text)
            
            # If surrogate is None, we skip masking (e.g. for generic Locations)
            if surrogate is None:
                continue

            # Store mapping (Surrogate -> Original)
            # We use the surrogate as the key for unmasking
            mapping[surrogate] = entity_text
            
            # Replace in text
            masked_text = masked_text[:result.start] + surrogate + masked_text[result.end:]
            
        return masked_text, mapping

    def mask_struct(self, data: Any, language: str = "en") -> Tuple[Any, Dict[str, str]]:
        """
        Recursively masks strings within a JSON-like structure (dict, list).
        
        Args:
            data: The data structure to mask (dict, list, or primitive).
            language: Language code for analysis (default: "en").
            
        Returns:
            A tuple of (masked_data, mapping) where mapping can restore originals.
        """
        combined_mapping = {}

        def recursive_mask(item):
            if isinstance(item, str):
                masked_val, mapping = self.mask(item, language=language)
                combined_mapping.update(mapping)
                return masked_val
            elif isinstance(item, dict):
                return {k: recursive_mask(v) for k, v in item.items()}
            elif isinstance(item, list):
                return [recursive_mask(i) for i in item]
            return item

        masked_data = recursive_mask(data)
        return masked_data, combined_mapping

    def unmask(self, masked_text: str, mapping: Dict[str, str]) -> str:
        """
        Restores the original text using the mapping.
        
        Args:
            masked_text: Text containing surrogate placeholders.
            mapping: Dictionary mapping surrogates to original values.
            
        Returns:
            The original text with all surrogates replaced.
        """
        unmasked_text = masked_text
        # Sort mapping keys by length descending to avoid partial replacements
        for surrogate, original in sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True):
            unmasked_text = unmasked_text.replace(surrogate, original)
        return unmasked_text

    # =========================================================================
    # Surrogate Generation Methods
    # =========================================================================
    
    # Country code to human-readable name mapping
    _COUNTRY_MAP: Dict[str, str] = {
        "DE": "German", "US": "US", "GB": "UK", "FR": "French",
        "ES": "Spanish", "IT": "Italian", "NL": "Dutch", "AT": "Austrian"
    }
    
    # Address indicators (street suffixes in various languages)
    _ADDRESS_INDICATORS: List[str] = [
        "street", "st.", "road", "rd.", "avenue", "ave.", "terrace", "lane",
        "drive", "way", "platz", "straße", "str.", "weg", "gasse", "allee"
    ]

    def _generate_surrogate(self, entity_type: str, value: str) -> Optional[str]:
        """
        Generate a context-preserving surrogate for a detected entity.
        
        Args:
            entity_type: The type of entity (e.g., "PERSON", "DATE_TIME").
            value: The actual entity value from the text.
            
        Returns:
            A surrogate string like "{Name_abc12}" or None to skip masking.
        """
        # Dispatch to specialized handlers
        handler = self._SURROGATE_HANDLERS.get(entity_type)
        if handler:
            return handler(self, value)
        
        # Check for compound entity types (e.g., DE_PASSPORT, US_DRIVER_LICENSE)
        if any(keyword in entity_type for keyword in ("PASSPORT", "DRIVER_LICENSE", "ID")):
            return self._surrogate_for_id_document(entity_type, value)
        
        # Default fallback: use entity type + hash
        return f"{{{entity_type}_{generate_hash_suffix(value, salt=self.seed)}}}"

    def _surrogate_for_person(self, value: str) -> str:
        """Generate surrogate for PERSON entities."""
        suffix = generate_hash_suffix(value, salt=self.seed)
        return f"{{Name_{suffix}}}"

    def _surrogate_for_date(self, value: str) -> str:
        """Generate surrogate for DATE_TIME entities."""
        return parse_and_format_date(value)

    def _surrogate_for_iban(self, value: str) -> str:
        """Generate surrogate for IBAN_CODE entities, preserving country context."""
        country_code = value[:2].upper()
        if country_code.isalpha():
            country_name = self._COUNTRY_MAP.get(country_code, country_code)
            return f"{{{country_name}_IBAN}}"
        return "{IBAN}"

    def _surrogate_for_german_id(self, value: str) -> str:
        """Generate surrogate for DE_ID_CARD entities."""
        return "{German_ID}"

    def _surrogate_for_id_document(self, entity_type: str, value: str) -> str:
        """
        Generate surrogate for passport/driver license/ID entities.
        
        Handles compound types like DE_PASSPORT, US_DRIVER_LICENSE.
        """
        parts = entity_type.split('_')
        if len(parts) > 1 and len(parts[0]) == 2:
            country_code = parts[0]
            country_name = self._COUNTRY_MAP.get(country_code, country_code)
            id_type = "_".join(parts[1:]).title()
            return f"{{{country_name}_{id_type}}}"
        return f"{{{entity_type}}}"

    def _surrogate_for_email(self, value: str) -> str:
        """Generate surrogate for EMAIL_ADDRESS entities, preserving domain."""
        if "@" in value:
            domain = value.split("@")[-1]
            return f"{{Email_at_{domain}}}"
        return "{Email}"

    def _surrogate_for_phone(self, value: str) -> str:
        """Generate surrogate for PHONE_NUMBER entities, preserving region."""
        try:
            parsed = phonenumbers.parse(value, None)
            region_code = phonenumbers.region_code_for_number(parsed)
            if region_code:
                return f"{{Phone_{region_code}}}"
        except phonenumbers.NumberParseException:
            pass
        return "{Phone}"

    def _surrogate_for_location(self, value: str) -> Optional[str]:
        """
        Generate surrogate for LOCATION entities.
        
        Only masks specific addresses (with street numbers/suffixes).
        Returns None for generic locations (cities, countries) to preserve context.
        """
        lower_val = value.lower()
        has_digits = any(char.isdigit() for char in value)
        has_address_indicator = any(ind in lower_val for ind in self._ADDRESS_INDICATORS)
        
        if has_digits or has_address_indicator:
            # It's a specific address - mask it
            if "," in value:
                # Try to extract city context from comma-separated address
                potential_city = value.split(',')[-1].strip()
                if potential_city and not any(c.isdigit() for c in potential_city) and potential_city[0].isupper():
                    return f"{{Address_in_{potential_city}}}"
            return f"{{Address_{generate_hash_suffix(value, salt=self.seed)}}}"
        
        # Generic location (city/country) - don't mask
        return None

    def _surrogate_for_nationality(self, value: str) -> str:
        """Generate surrogate for NRP (Nationality/Religious/Political) entities."""
        return f"{{Nationality_{generate_hash_suffix(value, salt=self.seed)}}}"

    # Handler dispatch table for cleaner routing
    _SURROGATE_HANDLERS: Dict[str, Callable[["PrivalyseMasker", str], Optional[str]]] = {
        "PERSON": _surrogate_for_person,
        "DATE_TIME": _surrogate_for_date,
        "IBAN_CODE": _surrogate_for_iban,
        "DE_ID_CARD": _surrogate_for_german_id,
        "EMAIL_ADDRESS": _surrogate_for_email,
        "PHONE_NUMBER": _surrogate_for_phone,
        "LOCATION": _surrogate_for_location,
        "NRP": _surrogate_for_nationality,
    }

    # =========================================================================
    # Overlap Resolution
    # =========================================================================

    def _remove_overlaps(self, results: List[RecognizerResult]) -> List[RecognizerResult]:
        """
        Remove overlapping entities using a greedy algorithm.
        
        When entities overlap, keeps the one with higher confidence score.
        If scores are equal, keeps the longer entity.
        
        Args:
            results: List of RecognizerResult from Presidio analysis.
            
        Returns:
            Filtered list with no overlapping entities.
        """
        if not results:
            return []
            
        # Sort by start index
        results.sort(key=lambda x: x.start)
        
        final_results = []
        if not results:
            return final_results
            
        current = results[0]
        
        for next_result in results[1:]:
            if next_result.start < current.end:
                # Overlap detected
                # Choose the one with higher score, or longer length if scores equal
                if next_result.score > current.score:
                    current = next_result
                elif next_result.score == current.score and (next_result.end - next_result.start) > (current.end - current.start):
                    current = next_result
                # Else keep current
            else:
                final_results.append(current)
                current = next_result
        
        final_results.append(current)
        return final_results

    def _merge_adjacent_dates(self, text: str, results: List[RecognizerResult]) -> List[RecognizerResult]:
        """
        Merge adjacent DATE_TIME entities separated only by whitespace/punctuation.
        
        Handles cases like "October 5th, 2025" which Presidio may detect as
        two separate entities ("October 5th" and "2025").
        
        Args:
            text: The original text being analyzed.
            results: List of RecognizerResult from Presidio analysis.
            
        Returns:
            List with adjacent dates merged into single entities.
        """
        if not results:
            return []
            
        # Sort by start index
        sorted_results = sorted(results, key=lambda x: x.start)
        merged_results = []
        
        current = sorted_results[0]
        
        for next_result in sorted_results[1:]:
            # Only merge DATE_TIME
            if current.entity_type == "DATE_TIME" and next_result.entity_type == "DATE_TIME":
                # Check gap
                gap = text[current.end:next_result.start]
                # If gap is small and only punctuation/space
                if len(gap) <= 3 and re.match(r"^[\s,.-]+$", gap):
                    # Merge: Extend current to cover next
                    current.end = next_result.end
                    # Keep max score
                    current.score = max(current.score, next_result.score)
                    continue
            
            merged_results.append(current)
            current = next_result
            
        merged_results.append(current)
        return merged_results
