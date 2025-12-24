from typing import Tuple, Dict, List, Optional, Union, Any
import logging
import phonenumbers
from enum import Enum
from dataclasses import dataclass, field
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from .utils import parse_and_format_date, generate_hash_suffix
from .recognizers import GermanIDRecognizer, SpacedIBANRecognizer, GermanAddressRecognizer, InternationalAddressRecognizer

logger = logging.getLogger(__name__)

class MaskingLevel(Enum):
    MASK_ALL = "mask_all"           # {PERSON}, {ADDRESS}
    MASK_WITH_HASH = "hash"         # {PERSON_a1b2}, {ADDRESS_c3d4}
    MASK_WITH_CONTEXT = "context"   # {Address_in_Berlin}, {Date_December_1990}
    PARTIAL_MASK = "partial"        # {Name_John_a1b2}, {Address_in_Berlin_Street_c3d4}
    KEEP_VISIBLE = "keep"           # No masking

@dataclass
class MaskingConfig:
    default_level: MaskingLevel = MaskingLevel.PARTIAL_MASK
    # Overrides per entity type (e.g. {"PERSON": MaskingLevel.MASK_WITH_HASH})
    entity_overrides: Dict[str, MaskingLevel] = field(default_factory=dict)
    
    def get_level(self, entity_type: str) -> MaskingLevel:
        return self.entity_overrides.get(entity_type, self.default_level)

class PrivalyseMasker:
    def __init__(self, languages: Optional[List[str]] = None, allow_list: List[str] = [], seed: str = "", config: Optional[MaskingConfig] = None):
        """
        Initialize the PrivalyseMasker.
        :param languages: List of languages for Presidio (e.g. ["en", "de"]). Defaults to all supported if None.
        :param allow_list: List of terms that should NEVER be masked (e.g. Company names)
        :param seed: Optional salt string to randomize hashes per project/session.
        :param config: Configuration for masking granularity.
        """
        self.allow_list = set(word.lower() for word in allow_list)
        self.seed = seed
        self.config = config or MaskingConfig()
        try:
            # Configure NLP Engine for multiple languages
            # We prefer 'lg' models but this requires them to be installed.
            # If not found, Presidio might raise an error.
            model_config = [
                {"lang_code": "en", "model_name": "en_core_web_lg"},
                {"lang_code": "de", "model_name": "de_core_news_lg"},
                {"lang_code": "fr", "model_name": "fr_core_news_lg"},
                {"lang_code": "es", "model_name": "es_core_news_lg"},
                {"lang_code": "it", "model_name": "it_core_news_lg"},
            ]
            
            # If languages is None, use all available in model_config
            if languages is None:
                languages = [m["lang_code"] for m in model_config]
            
            # Filter for requested languages
            active_models = [m for m in model_config if m["lang_code"] in languages]
            
            if not active_models:
                # Fallback to default (usually just EN)
                self.analyzer = AnalyzerEngine()
            else:
                provider = NlpEngineProvider(nlp_configuration={
                    "nlp_engine_name": "spacy", 
                    "models": active_models
                })
                nlp_engine = provider.create_engine()
                self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=languages)

            # Add custom recognizers for each supported language
            # These patterns are specific (e.g. German Address format) but can appear in any language context
            for lang in languages:
                self.analyzer.registry.add_recognizer(GermanIDRecognizer(supported_language=lang))
                self.analyzer.registry.add_recognizer(SpacedIBANRecognizer(supported_language=lang))
                self.analyzer.registry.add_recognizer(GermanAddressRecognizer(supported_language=lang))
                self.analyzer.registry.add_recognizer(InternationalAddressRecognizer(supported_language=lang))
        except Exception as e:
            logger.warning(f"Failed to initialize AnalyzerEngine: {e}")
            logger.warning("Ensure you have installed 'presidio-analyzer' and downloaded spacy models (e.g. en_core_web_lg, de_core_news_lg).")
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

    def mask_struct(self, data: any, language: str = "en") -> Tuple[any, Dict[str, str]]:
        """
        Recursively masks strings within a JSON-like structure (dict, list).
        Returns the masked structure and a combined mapping.
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
        """
        unmasked_text = masked_text
        # Sort mapping keys by length descending to avoid partial replacements if any
        for surrogate, original in sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True):
            unmasked_text = unmasked_text.replace(surrogate, original)
        return unmasked_text

    def _generate_surrogate(self, entity_type: str, value: str) -> Optional[str]:
        level = self.config.get_level(entity_type)
        
        if level == MaskingLevel.KEEP_VISIBLE:
            return None
            
        if level == MaskingLevel.MASK_ALL:
            return f"{{{entity_type}}}"
            
        if level == MaskingLevel.MASK_WITH_HASH:
            suffix = generate_hash_suffix(value, salt=self.seed)
            return f"{{{entity_type}_{suffix}}}"

        # --- PERSON ---
        if entity_type == "PERSON":
            suffix = generate_hash_suffix(value, salt=self.seed)
            
            if level == MaskingLevel.PARTIAL_MASK:
                # "Prename within the Mask" -> {User_<Hash>_Prename_<Name>}
                # Heuristic: First token is First Name
                parts = value.split()
                if len(parts) > 0:
                    first_name = parts[0]
                    # Ensure first name is not just an initial or title
                    if len(first_name) > 1 and first_name[0].isupper():
                        return f"{{User_{suffix}_Prename_{first_name}}}"
            
            # Default Context/Hash behavior
            return f"{{User_{suffix}}}"
        
        # --- DATE ---
        elif entity_type == "DATE_TIME":
            # Context: {Date_December_1990}
            return parse_and_format_date(value)
            
        # --- IBAN ---
        elif entity_type == "IBAN_CODE":
            # Extract country code (first 2 chars usually)
            country_code = value[:2].upper()
            if country_code.isalpha():
                country_map = {"DE": "German", "US": "US", "GB": "UK", "FR": "French"}
                country_name = country_map.get(country_code, country_code)
                return f"{{{country_name}_IBAN}}"
            return "{IBAN}"

        # --- ID CARDS ---
        elif entity_type == "DE_ID_CARD":
            return "{German_ID}"
            
        elif "PASSPORT" in entity_type or "DRIVER_LICENSE" in entity_type or "ID" in entity_type:
             parts = entity_type.split('_')
             if len(parts) > 1 and len(parts[0]) == 2:
                 country_code = parts[0]
                 country_map = {"DE": "German", "US": "US", "GB": "UK", "FR": "French"}
                 country_name = country_map.get(country_code, country_code)
                 id_type = "_".join(parts[1:]).title() # Passport, Driver_License
                 return f"{{{country_name}_{id_type}}}"
             return f"{{{entity_type}}}"
             
        # --- EMAIL ---
        elif entity_type == "EMAIL_ADDRESS":
             if "@" in value:
                 domain = value.split("@")[-1]
                 return f"{{Email_at_{domain}}}"
             return "{Email}"

        # --- PHONE ---
        elif entity_type == "PHONE_NUMBER":
             try:
                 parsed = phonenumbers.parse(value, None)
                 region_code = phonenumbers.region_code_for_number(parsed)
                 if region_code:
                     return f"{{Phone_{region_code}}}"
             except:
                 pass
             return "{Phone}"
             
        # --- ADDRESS ---
        elif entity_type == "ADDRESS":
             # PARTIAL_MASK: {Address_in_Berlin_Street_<Hash>}
             # CONTEXT: {Address_in_Berlin}
             
             city = None
             # Try to extract city context
             if "," in value:
                 parts = value.split(',')
                 # Case 1: "Berlin, Alexanderplatz 1" -> City is first
                 first_part = parts[0].strip()
                 if not any(char.isdigit() for char in first_part) and first_part[0].isupper():
                     city = first_part
                 else:
                     # Case 2: "Musterstraße 42, Munich" -> City is last
                     last_part = parts[-1].strip()
                     last_part_no_zip = " ".join([w for w in last_part.split() if not w.isdigit()])
                     if last_part_no_zip and last_part_no_zip[0].isupper():
                         city = last_part_no_zip
             
             suffix = generate_hash_suffix(value, salt=self.seed)
             
             if city:
                 if level == MaskingLevel.PARTIAL_MASK:
                     # Keep City visible, mask street with hash
                     return f"{{Address_in_{city}_Street_{suffix}}}"
                 else:
                     # Just City context
                     return f"{{Address_in_{city}}}"
             
             return f"{{Address_{suffix}}}"

        # --- LOCATION (Generic) ---
        elif entity_type == "LOCATION":
             # Heuristic: If it contains digits, it's likely a specific address
             address_indicators = ["street", "st.", "road", "rd.", "avenue", "ave.", "terrace", "lane", "drive", "way", "platz", "straße", "str.", "weg", "gasse", "allee"]
             lower_val = value.lower()
             
             is_address = any(char.isdigit() for char in value) or any(ind in lower_val for ind in address_indicators)
             
             if is_address:
                 # Treat as Address
                 if "," in value:
                     parts = value.split(',')
                     potential_city = parts[-1].strip()
                     if potential_city and not any(char.isdigit() for char in potential_city) and potential_city[0].isupper():
                         if level == MaskingLevel.PARTIAL_MASK:
                             suffix = generate_hash_suffix(value, salt=self.seed)
                             return f"{{Address_in_{potential_city}_Street_{suffix}}}"
                         return f"{{Address_in_{potential_city}}}"
                 
                 return f"{{Address_{generate_hash_suffix(value, salt=self.seed)}}}"
             else:
                 # Generic Location (City/Country) -> Keep visible by default unless MASK_ALL
                 if level == MaskingLevel.MASK_ALL:
                     return "{Location}"
                 return None

        elif entity_type == "NRP":
             return f"{{Nationality_{generate_hash_suffix(value, salt=self.seed)}}}"
             
        # Default fallback
        return f"{{{entity_type}_{generate_hash_suffix(value, salt=self.seed)}}}"

    def _remove_overlaps(self, results):
        """
        Remove overlapping entities, preferring higher score or longer length.
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
