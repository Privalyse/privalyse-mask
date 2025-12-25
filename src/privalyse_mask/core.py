from typing import Tuple, Dict, List, Optional
import logging
import re
import phonenumbers
from presidio_analyzer import AnalyzerEngine
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
    def __init__(self, languages: List[str] = ["en", "de"], allow_list: List[str] = [], seed: str = ""):
        """
        Initialize the PrivalyseMasker.
        :param languages: List of languages for Presidio (e.g. ["en", "de"])
        :param allow_list: List of terms that should NEVER be masked (e.g. Company names)
        :param seed: Optional salt string to randomize hashes per project/session.
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
            
            # Map common languages to their large spacy models
            model_map = {
                "en": "en_core_web_lg",
                "de": "de_core_news_lg",
                "es": "es_core_news_lg",
                "fr": "fr_core_news_lg",
                "it": "it_core_news_lg"
            }
            
            for lang in languages:
                model_name = model_map.get(lang, f"{lang}_core_web_lg") # Fallback
                nlp_configuration["models"].append({"lang_code": lang, "model_name": model_name})

            provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
            nlp_engine = provider.create_engine()
            
            self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=languages)
            # Add custom recognizers
            print("DEBUG: Adding custom recognizers...")
            
            for lang in languages:
                self.analyzer.registry.add_recognizer(GermanIDRecognizer(supported_language=lang))
                self.analyzer.registry.add_recognizer(SpacedIBANRecognizer(supported_language=lang))
            
            print(f"DEBUG: Registry size: {len(self.analyzer.registry.recognizers)}")
        except Exception as e:
            logger.warning(f"Failed to initialize AnalyzerEngine: {e}")
            logger.warning("Ensure you have installed 'presidio-analyzer' and downloaded spacy models.")
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

    def _generate_surrogate(self, entity_type: str, value: str) -> str:
        if entity_type == "PERSON":
            suffix = generate_hash_suffix(value, salt=self.seed)
            return f"{{Name_{suffix}}}"
        
        elif entity_type == "DATE_TIME":
            return parse_and_format_date(value)
            
        elif entity_type == "IBAN_CODE":
            # Extract country code (first 2 chars usually)
            country_code = value[:2].upper()
            if country_code.isalpha():
                # Map common codes to full names if desired, or keep code
                # User asked for {German_IBAN} for DE
                country_map = {"DE": "German", "US": "US", "GB": "UK", "FR": "French"}
                country_name = country_map.get(country_code, country_code)
                return f"{{{country_name}_IBAN}}"
            return "{IBAN}"

        elif entity_type == "DE_ID_CARD":
            return "{German_ID}"
            
        elif "PASSPORT" in entity_type or "DRIVER_LICENSE" in entity_type or "ID" in entity_type:
             # Handle DE_PASSPORT, US_PASSPORT etc.
             # If type is like DE_PASSPORT, we want {German_Passport} or {German_ID}
             parts = entity_type.split('_')
             if len(parts) > 1 and len(parts[0]) == 2:
                 country_code = parts[0]
                 country_map = {"DE": "German", "US": "US", "GB": "UK", "FR": "French"}
                 country_name = country_map.get(country_code, country_code)
                 id_type = "_".join(parts[1:]).title() # Passport, Driver_License
                 return f"{{{country_name}_{id_type}}}"
             
             # Fallback for generic ID types detected by Presidio (like US_DRIVER_LICENSE without underscore sometimes?)
             # Actually Presidio uses US_DRIVER_LICENSE.
             return f"{{{entity_type}}}"
             
        elif entity_type == "EMAIL_ADDRESS":
             # Preserve domain for context (Business vs Personal)
             if "@" in value:
                 domain = value.split("@")[-1]
                 return f"{{Email_at_{domain}}}"
             return "{Email}"

        elif entity_type == "PHONE_NUMBER":
             # Try to extract region/country
             try:
                 # Assume generic parsing if no region provided, or try to infer
                 parsed = phonenumbers.parse(value, None)
                 region_code = phonenumbers.region_code_for_number(parsed)
                 if region_code:
                     return f"{{Phone_{region_code}}}"
             except:
                 pass
             return "{Phone}"
             
        elif entity_type == "LOCATION":
             # Heuristic: If it contains digits, it's likely a specific address (Street + Number)
             # Or if it contains common street suffixes
             address_indicators = ["street", "st.", "road", "rd.", "avenue", "ave.", "terrace", "lane", "drive", "way", "platz", "straße", "str.", "weg", "gasse", "allee"]
             lower_val = value.lower()
             
             is_address = any(char.isdigit() for char in value) or any(ind in lower_val for ind in address_indicators)
             
             if is_address:
                 # Try to extract city context from the address string itself
                 # Heuristic: If comma separated, last part is often City/State/Country
                 if "," in value:
                     parts = value.split(',')
                     potential_city = parts[-1].strip()
                     # If it looks like a city (no digits, starts with upper case)
                     if potential_city and not any(char.isdigit() for char in potential_city) and potential_city[0].isupper():
                         return f"{{Address_in_{potential_city}}}"
                 
                 return f"{{Address_{generate_hash_suffix(value, salt=self.seed)}}}"
             else:
                 # Return None to indicate "do not mask" (Keep Cities/Countries)
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

    def _merge_adjacent_dates(self, text: str, results: List) -> List:
        """
        Merges adjacent DATE_TIME entities if they are separated only by spaces/punctuation.
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
