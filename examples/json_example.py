import sys
import os
import json

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from privalyse_mask import PrivalyseMasker

def main():
    print("🕵️  Privalyse Mask - Agent/JSON Example")
    print("=======================================")

    # 1. Initialize with Allow List
    # We don't want to mask "Privalyse" or "TechCorp" even if they look like names/orgs
    masker = PrivalyseMasker(languages=["en"], allow_list=["TechCorp", "Privalyse"])

    # 2. Complex JSON Input (e.g. from a Tool Call or API)
    user_data = {
        "user_id": 12345,
        "profile": {
            "full_name": "Peter Parker",
            "bio": "Software Engineer at TechCorp. Born on 12.10.1995.",
            "contact": {
                "email": "peter.parker@techcorp.com",
                "phone": "+1 555 0102"
            }
        },
        "transactions": [
            {"id": "TX99", "recipient": "Mary Jane", "iban": "US12 3456 7890"},
            {"id": "TX100", "recipient": "TechCorp Payroll", "amount": 5000}
        ]
    }

    print(f"\n[Original JSON]:\n{json.dumps(user_data, indent=2)}")

    # 3. Mask Structure
    print("\n[Masking Structure]...")
    masked_data, mapping = masker.mask_struct(user_data)

    print(f"\n[Masked JSON sent to LLM]:\n{json.dumps(masked_data, indent=2)}")
    print(f"\n[Mapping]:\n{mapping}")

    # 4. Simulate LLM processing the JSON
    # The LLM might return a new JSON based on the masked data
    print("\n[Simulating LLM Agent Response]...")
    
    # LLM creates a summary object
    llm_response_obj = {
        "summary": f"User {masked_data['profile']['full_name']} works at TechCorp.",
        "financial_alert": f"Payment to {masked_data['transactions'][0]['recipient']} ({masked_data['transactions'][0]['iban']}) detected.",
        "next_action": "Verify ID"
    }
    
    print(f"\n[LLM Response Object]:\n{json.dumps(llm_response_obj, indent=2)}")

    # 5. Unmask Structure (works on Dicts too!)
    # We can use a helper to unmask a struct, or just unmask strings.
    # Let's add a helper for unmasking structs to core.py? 
    # For now, let's just unmask the strings we care about or the whole dump.
    
    # Option A: Unmask the string dump (easiest for display)
    unmasked_str = masker.unmask(json.dumps(llm_response_obj), mapping)
    print(f"\n[Final Unmasked JSON String]:\n{unmasked_str}")

if __name__ == "__main__":
    main()
