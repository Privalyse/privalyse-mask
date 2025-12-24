import sys
import os
from typing import List, Tuple

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from privalyse_mask import PrivalyseMasker

def run_stress_test():
    masker = PrivalyseMasker(languages=["en", "de"])
    
    test_cases = [
        # Standard German Addresses
        ("I live in Berlin, Alexanderplatz 1.", "{Address_in_Berlin}"),
        ("Meeting at Musterstraße 42, Munich.", "{Address_in_Munich}"),
        ("Go to Unter den Linden 5.", "{Address_...}"), # No city context
        ("My office is at Hauptstr. 10.", "{Address_...}"),
        
        # Variations
        ("Living at Kurfürstendamm 123a.", "{Address_...}"), # Number with letter
        ("Address: Am Wasserturm 5-7.", "{Address_...}"), # Number range
        ("Visit me at Schlossallee 1, 12345 Entenhausen.", "{Address_in_Entenhausen}"), # With Zip
        
        # Edge Cases / False Positives
        ("I bought 5 apples.", "I bought 5 apples."), # Should NOT mask
        ("Room 42 is open.", "Room 42 is open."), # Should NOT mask
        ("It happened on March 1.", "It happened on March 1."), # Date, not address
        
        # Complex Context
        ("Send it to Hamburg, Reeperbahn 1.", "{Address_in_Hamburg}"),
        ("Frankfurt am Main, Zeil 10.", "{Address_in_Frankfurt am Main}"),
    ]

    print("🏗️  Running Address Stress Test...")
    print("================================")
    
    failures = 0
    for input_text, expected_hint in test_cases:
        masked, _ = masker.mask(input_text)
        
        # Check if it was masked at all
        was_masked = "Address" in masked or "Location" in masked
        
        # Check if specific hint is present (if expected)
        hint_present = True
        if expected_hint != "{Address_...}" and expected_hint not in input_text:
             # If we expect a specific surrogate like {Address_in_Berlin}
             # We check if that string is in the output
             if expected_hint not in masked:
                 hint_present = False
        
        # Determine status
        # If we expected NO masking (input == output)
        if input_text == expected_hint:
            if masked == input_text:
                status = "✅ PASS (Ignored)"
            else:
                status = f"❌ FAIL (Over-masked: {masked})"
                failures += 1
        else:
            # We expected masking
            if was_masked and hint_present:
                status = "✅ PASS"
            elif was_masked and not hint_present:
                status = f"⚠️  PARTIAL (Masked but wrong context: {masked})"
                failures += 1
            else:
                status = f"❌ FAIL (Not masked: {masked})"
                failures += 1
                
        print(f"\nInput:    {input_text}")
        print(f"Output:   {masked}")
        print(f"Status:   {status}")

    print(f"\nTotal Failures/Warnings: {failures}")

if __name__ == "__main__":
    run_stress_test()
