import sys
import os
import time
import json
import random
import string
from typing import List, Dict, Any
from dataclasses import dataclass

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from privalyse_mask import PrivalyseMasker

@dataclass
class BenchmarkResult:
    name: str
    score: float
    metric: str
    details: Dict[str, Any]

class ComprehensiveBenchmark:
    def __init__(self):
        print("🔧 Initializing PrivalyseMasker...")
        self.masker = PrivalyseMasker(languages=["en"])
        self.results: List[BenchmarkResult] = []

    def _generate_synthetic_data(self, num_samples=100) -> List[str]:
        """Generates synthetic PII-heavy text."""
        samples = []
        templates = [
            "My name is {name} and I live in {city}.",
            "Contact me at {email} or call {phone}.",
            "I was born on {date}.",
            "My IBAN is {iban}.",
            "Please send the package to {address}."
        ]
        
        # Simple pools
        names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank"]
        cities = ["Berlin", "New York", "London", "Paris", "Tokyo"]
        emails = ["test@example.com", "user@company.org", "contact@mail.net"]
        phones = ["+1-555-0100", "+49-30-123456", "07700 900077"]
        dates = ["12.10.1990", "January 1st, 2000", "2023-05-20"]
        ibans = ["DE89 3704 0044 0532 0130 00", "GB29 XANA 1020 3012 3456 78"]
        addresses = ["123 Main St", "42 Wallaby Way", "10 Downing Street"]

        for _ in range(num_samples):
            tmpl = random.choice(templates)
            text = tmpl.format(
                name=random.choice(names),
                city=random.choice(cities),
                email=random.choice(emails),
                phone=random.choice(phones),
                date=random.choice(dates),
                iban=random.choice(ibans),
                address=random.choice(addresses)
            )
            samples.append(text)
        return samples

    def run_consistency_test(self):
        """
        Checks if unmask(mask(text)) == text.
        This is critical for the 'Seamless Restoration' promise.
        """
        print("\n🔄 Running Consistency (Round-Trip) Benchmark...")
        samples = self._generate_synthetic_data(50)
        passed = 0
        failures = []

        for text in samples:
            masked, mapping = self.masker.mask(text)
            restored = self.masker.unmask(masked, mapping)
            
            if restored == text:
                passed += 1
            else:
                failures.append({
                    "original": text,
                    "masked": masked,
                    "restored": restored
                })

        score = (passed / len(samples)) * 100
        self.results.append(BenchmarkResult(
            name="Consistency (Round-Trip)",
            score=score,
            metric="Accuracy %",
            details={"failures": failures[:3]} # Log top 3 failures
        ))
        print(f"   Score: {score:.1f}%")

    def run_performance_test(self):
        """
        Measures throughput in characters per second.
        """
        print("\n⚡ Running Performance Benchmark...")
        samples = self._generate_synthetic_data(200)
        total_chars = sum(len(s) for s in samples)
        
        start_time = time.time()
        for text in samples:
            self.masker.mask(text)
        end_time = time.time()
        
        duration = end_time - start_time
        throughput = total_chars / duration
        
        self.results.append(BenchmarkResult(
            name="Performance",
            score=throughput,
            metric="Chars/sec",
            details={"total_chars": total_chars, "duration_s": duration}
        ))
        print(f"   Throughput: {throughput:.0f} chars/sec")

    def run_context_preservation_test(self):
        """
        Checks if semantic context is preserved in surrogates using Heuristic Analysis.
        
        NOTE: This does NOT query an actual LLM (like GPT-4). 
        Instead, it uses 'Proxy Metrics' to estimate utility.
        
        Theory:
        If the masked string contains specific semantic tokens (e.g. "1990", "October"),
        we assume an LLM *could* use that context.
        
        Example:
        - Input: "Born in 1990"
        - Masked: "{Date_1990}" -> Contains "1990" -> PASS
        - Masked: "{Date_REDACTED}" -> Missing "1990" -> FAIL
        
        This allows for fast, deterministic, and free benchmarking without API costs.
        """
        print("\n🧠 Running Context Preservation Benchmark (Heuristic/Proxy)...")
        
        # Define test cases: (Input Text, Token that MUST exist in masked output)
        test_cases = [
            ("I was born in 1990", "1990"),      # Year should be preserved
            ("Meeting in October", "October"),   # Month should be preserved
            ("My name is Alice", "Name"),        # Entity Type should be visible
        ]
        
        passed = 0
        for text, expected_context in test_cases:
            masked, _ = self.masker.mask(text)
            
            # HEURISTIC CHECK:
            # We search for the 'expected_context' substring within the 'masked' output.
            # If it exists, we assume the surrogate successfully encoded the context.
            if expected_context.lower() in masked.lower():
                passed += 1
            else:
                # Fallback: Check for generic type indicators if specific value is hidden
                if expected_context == "Name" and ("PERSON" in masked or "Name" in masked):
                    passed += 1
                else:
                    print(f"   ❌ Failed: '{text}' -> '{masked}' (Missing: '{expected_context}')")
        
        score = (passed / len(test_cases)) * 100
        self.results.append(BenchmarkResult(
            name="Context Preservation (Proxy)",
            score=score,
            metric="Score %",
            details={}
        ))
        print(f"   Score: {score:.1f}%")

    def print_summary(self):
        print("\n📊 FINAL BENCHMARK SUMMARY")
        print("==========================")
        for res in self.results:
            print(f"{res.name}: {res.score:.2f} {res.metric}")
            if res.details.get("failures"):
                print("   ⚠️ Failures detected (first 3):")
                for f in res.details["failures"]:
                    print(f"     - Orig: {f['original']}")
                    print(f"       Rest: {f['restored']}")

if __name__ == "__main__":
    bench = ComprehensiveBenchmark()
    bench.run_consistency_test()
    bench.run_performance_test()
    bench.run_context_preservation_test()
    bench.print_summary()
