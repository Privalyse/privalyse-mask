import sys
import os
from typing import List, Tuple, Optional

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from privalyse_mask import PrivalyseMasker

def run_multilingual_stress_test():
    print("🌍 Initializing Multilingual PrivalyseMasker (EN, DE, FR)...")
    masker = PrivalyseMasker(languages=["en", "de", "fr"])
    
    # Format: (Language, Input Text, Expected Output Substring, Description)
    test_cases = [
        # --- GERMAN (DE) ---
        ("de", "Ich wohne in Berlin, Alexanderplatz 1.", "{Address_in_Berlin}", "DE Address (City Prefix)"),
        ("de", "Mein Büro ist in der Musterstraße 42, München.", "{Address_in_Munich}", "DE Address (City Suffix)"), # Presidio might see München as Munich
        ("de", "Treffen wir uns in der Hauptstr. 5.", "{Address_", "DE Address (Strict)"),
        ("de", "Meine IBAN ist DE89 3704 0044 0532 0130 00.", "{German_IBAN}", "DE IBAN (Spaced)"),
        ("de", "Geboren am 24.12.1990.", "1990", "DE Date (DD.MM.YYYY)"),
        ("de", "Ruf mich an unter +49 30 1234567.", "{Phone", "DE Phone"),
        ("de", "Mein Name ist Max Mustermann.", "{Name_", "DE Name"),

        # --- ENGLISH (EN/US/UK) ---
        ("en", "I live at 123 Main St, New York, NY.", "{Address", "US Address"),
        ("en", "Visit 10 Downing Street, London.", "{Address", "UK Address"),
        ("en", "My email is john.doe@example.com.", "{Email_at_example.com}", "Email Context"),
        ("en", "Call me at +1-212-555-0199.", "{Phone", "US Phone"),
        ("en", "Born on 10/12/1980.", "1980", "US Date (MM/DD/YYYY)"),
        ("en", "My name is John Smith.", "{Name_", "EN Name"),

        # --- FRENCH (FR) ---
        ("fr", "J'habite au 10 Rue de la Paix, Paris.", "{Address", "FR Address"), # Might need custom recognizer or rely on Location
        ("fr", "Mon numéro est +33 6 12 34 56 78.", "{Phone", "FR Phone"),
        ("fr", "Je m'appelle Jean Dupont.", "{Name_", "FR Name"),
        ("fr", "Né le 14 juillet 1789.", "1789", "FR Date"),
        
        # --- EDGE CASES & FALSE POSITIVES ---
        ("en", "I bought 5 apples.", "I bought 5 apples.", "False Positive: Number"),
        ("de", "Ich habe 3 Kinder.", "Ich habe 3 Kinder.", "False Positive: Number DE"),
        ("en", "Version 2.0 is out.", "Version 2.0 is out.", "False Positive: Version"),
        ("en", "Go to http://example.com/page/1", "{URL_", "URL Preservation (or Masking?)"), # URLs usually masked or kept? Presidio detects URLs.
    ]

    print("\n🚀 Running Multilingual Stress Test...")
    print("======================================")
    
    passed = 0
    warnings = 0
    failures = 0
    
    for lang, input_text, expected, desc in test_cases:
        masked, _ = masker.mask(input_text, language=lang)
        
        # Logic for Pass/Fail
        is_pass = False
        status_msg = ""
        
        # Case 1: We expect NO change (False Positive check)
        if input_text == expected:
            if masked == input_text:
                is_pass = True
                status_msg = "✅ PASS"
            else:
                is_pass = False
                status_msg = f"❌ FAIL (Over-masked: {masked})"
        
        # Case 2: We expect masking containing a specific substring
        else:
            if expected in masked:
                is_pass = True
                status_msg = "✅ PASS"
            else:
                # Check if it was masked at all but differently
                if masked != input_text:
                    is_pass = False
                    status_msg = f"⚠️  WARN (Masked but missing '{expected}': {masked})"
                else:
                    is_pass = False
                    status_msg = f"❌ FAIL (Not masked)"

        if is_pass:
            passed += 1
        elif "WARN" in status_msg:
            warnings += 1
        else:
            failures += 1
            
        print(f"\n[{lang.upper()}] {desc}")
        print(f"  In:  {input_text}")
        print(f"  Out: {masked}")
        print(f"  {status_msg}")

    print("\n📊 Summary")
    print(f"Passed:   {passed}")
    print(f"Warnings: {warnings}")
    print(f"Failures: {failures}")
    print(f"Total:    {len(test_cases)}")

if __name__ == "__main__":
    run_multilingual_stress_test()
