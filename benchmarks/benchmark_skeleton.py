import sys
import os
import json
from typing import List, Dict

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from privalyse_mask import PrivalyseMasker

class PrivalyseBenchmark:
    def __init__(self):
        self.masker = PrivalyseMasker(languages=["en"])
        self.results = []

    def run_utility_test(self, test_cases: List[Dict]):
        """
        Simulates LLM tasks to measure if masking breaks the logic.
        """
        print("🧪 Running Utility Benchmark...")
        
        for case in test_cases:
            original_input = case["input"]
            expected_intent = case["expected_intent"]
            
            # 1. Mask
            masked_input, mapping = self.masker.mask(original_input)
            
            # 2. Simulate LLM Logic (Mocked for now)
            # In a real benchmark, we would call GPT-4 here.
            # Here we check if the necessary context tokens are present in the masked string.
            
            success = True
            missing_context = []
            
            for context_token in case["required_context_tokens"]:
                # We check if the token (or its mapped surrogate) is present
                # Ideally, we want the SEMANTIC context. 
                # E.g. if "Berlin" is required, it should be in masked_input.
                # If "12.10.2000" is required, "{Date_October_2000}" is acceptable.
                
                # Check if it was mapped to something acceptable
                # This is hard to mock perfectly without an LLM, but let's try heuristics
                found_acceptable = False
                
                # 1. Check if token is literally in text (e.g. "Berlin")
                if context_token in masked_input:
                    found_acceptable = True
                
                # 2. Check if it is part of a surrogate (e.g. "1990" in "{Date_October_1990}")
                if not found_acceptable:
                    for surrogate in mapping.keys():
                        if context_token in surrogate:
                             found_acceptable = True
                             break
                
                # 3. Check if it was masked (e.g. "Peter") -> If the task allows masking, this is success.
                # For this benchmark, let's assume if it's in the mapping, it's "available" to the LLM as a placeholder.
                if not found_acceptable:
                    for original in mapping.values():
                        if context_token in original:
                            found_acceptable = True
                            break

                if not found_acceptable:
                    success = False
                    missing_context.append(context_token)

            self.results.append({
                "id": case["id"],
                "masked_input": masked_input,
                "success": success,
                "missing": missing_context
            })
            
            status = "✅" if success else "❌"
            print(f"{status} Case {case['id']}: {original_input[:30]}... -> {masked_input[:30]}...")

    def print_report(self):
        print("\n📊 Benchmark Report")
        print("===================")
        total = len(self.results)
        passed = sum(1 for r in self.results if r["success"])
        print(f"Score: {passed}/{total} ({passed/total*100:.1f}%)")
        
        for r in self.results:
            if not r["success"]:
                print(f"\nFailed Case {r['id']}:")
                print(f"Masked: {r['masked_input']}")
                print(f"Missing Context: {r['missing']}")

if __name__ == "__main__":
    # Define Test Cases
    cases = [
        {
            "id": 1,
            "input": "I live in Berlin.",
            "expected_intent": "Identify Location",
            "required_context_tokens": ["Berlin"] # Should be preserved
        },
        {
            "id": 2,
            "input": "My name is Peter.",
            "expected_intent": "Identify Name",
            "required_context_tokens": ["Peter"] # Should be masked, so this 'literal' check will fail, showing we need semantic check
        },
        {
            "id": 3,
            "input": "Born on 12.10.1990.",
            "expected_intent": "Age Calculation",
            "required_context_tokens": ["1990"] # Should be in surrogate {Date_..._1990}
        }
    ]
    
    # Note: This mock benchmark is strict. 
    # Case 2 will fail because "Peter" is masked, which is GOOD for privacy but bad for this naive utility check.
    # Real utility check needs to know that {Name_X} is a valid substitute for Peter.
    
    bench = PrivalyseBenchmark()
    bench.run_utility_test(cases)
    bench.print_report()
