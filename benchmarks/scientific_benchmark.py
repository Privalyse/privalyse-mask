import sys
import os
import random
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from faker import Faker

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from privalyse_mask import PrivalyseMasker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("ScientificBenchmark")

@dataclass
class LabeledSample:
    text: str
    pii_spans: List[Tuple[int, int, str]]  # (start, end, type)
    pii_values: List[str]

class PrivacyEvaluator:
    """
    Measures HOW WELL we detect PII (Recall) and if we mask too much (Precision).
    Uses synthetic data generation where we KNOW the ground truth.
    """
    def __init__(self):
        self.fake = Faker()
        self.masker = PrivalyseMasker(languages=["en"])

    def generate_labeled_data(self, num_samples=100) -> List[LabeledSample]:
        """
        Generates sentences with KNOWN PII positions.
        """
        samples = []
        # Templates where we inject PII
        templates = [
            ("My name is {name}.", "PERSON"),
            ("I live in {city}.", "LOCATION"),
            ("Contact {email} for details.", "EMAIL_ADDRESS"),
            ("Call me at {phone}.", "PHONE_NUMBER"),
            ("My IBAN is {iban}.", "IBAN"),
        ]

        for _ in range(num_samples):
            tmpl, pii_type = random.choice(templates)
            
            # Generate value based on type
            if pii_type == "PERSON":
                val = self.fake.name()
            elif pii_type == "LOCATION":
                val = self.fake.city()
            elif pii_type == "EMAIL_ADDRESS":
                val = self.fake.email()
            elif pii_type == "PHONE_NUMBER":
                val = self.fake.phone_number()
            elif pii_type == "IBAN":
                val = self.fake.iban()
            
            # Construct text
            text = tmpl.format(name=val, city=val, email=val, phone=val, iban=val)
            
            # Find position (simplified assumption: value appears once)
            start = text.find(val)
            end = start + len(val)
            
            samples.append(LabeledSample(
                text=text,
                pii_spans=[(start, end, pii_type)],
                pii_values=[val]
            ))
        return samples

    def evaluate(self, samples: List[LabeledSample]):
        print("\n🛡️  Running Privacy Evaluation (Recall/Precision)...")
        
        true_positives = 0  # PII correctly masked
        false_negatives = 0 # PII missed (Leak!)
        # Note: False Positives are harder to measure without full sentence labeling, 
        # but we can check if non-PII words were masked.

        for sample in samples:
            masked_text, mapping = self.masker.mask(sample.text)
            
            # Check each known PII value
            for pii_val in sample.pii_values:
                if pii_val not in masked_text:
                    # The value is GONE from the text -> Successfully Masked
                    true_positives += 1
                else:
                    # The value is STILL in the text -> Leak
                    # Edge case: Sometimes the surrogate contains the value (e.g. City names)
                    # We need to check if it's inside a surrogate or raw.
                    
                    # Simple check: Is it in the mapping values?
                    # If it's in the mapping, it was detected.
                    if pii_val in mapping.values():
                        true_positives += 1
                    else:
                        false_negatives += 1
                        # logger.warning(f"Leak detected: '{pii_val}' in '{masked_text}'")

        total_pii = true_positives + false_negatives
        recall = true_positives / total_pii if total_pii > 0 else 0
        
        print(f"   Samples: {len(samples)}")
        print(f"   Recall: {recall:.2%} (Higher is better - means we caught the PII)")
        if recall < 1.0:
            print(f"   ⚠️  Missed {false_negatives} PII entities!")

class UtilityEvaluator:
    """
    Measures if the masked text is still USEFUL for an LLM.
    Simulates an 'Intent Classification' or 'Extraction' task.
    """
    def __init__(self):
        self.masker = PrivalyseMasker(languages=["en"])

    def mock_llm_extract_intent(self, text: str) -> str:
        """
        Simulates an LLM that tries to understand the text.
        In a real benchmark, this would be `openai.ChatCompletion.create(...)`.
        """
        text_lower = text.lower()
        if "flight" in text_lower or "fly" in text_lower:
            return "book_flight"
        if "meeting" in text_lower or "schedule" in text_lower:
            return "schedule_meeting"
        if "refund" in text_lower or "money" in text_lower:
            return "request_refund"
        return "unknown"

    def run_benchmark(self):
        print("\n🤖 Running Utility Evaluation (Simulated LLM Task)...")
        
        # Dataset: (Original Text, Expected Intent)
        dataset = [
            ("I want to book a flight to Berlin.", "book_flight"),
            ("Schedule a meeting with Alice on Monday.", "schedule_meeting"),
            ("I need a refund for my order #123.", "request_refund"),
            ("Can you fly me to New York?", "book_flight"),
            ("Where is my money?", "request_refund")
        ]
        
        original_score = 0
        masked_score = 0
        
        for text, expected in dataset:
            # 1. Baseline (Original)
            pred_orig = self.mock_llm_extract_intent(text)
            if pred_orig == expected:
                original_score += 1
                
            # 2. Masked
            masked_text, _ = self.masker.mask(text)
            pred_masked = self.mock_llm_extract_intent(masked_text)
            
            # Does the LLM still understand the intent even with surrogates?
            # e.g. "Schedule a meeting with {Name_...} on {Date_...}" -> "schedule_meeting"
            if pred_masked == expected:
                masked_score += 1
            else:
                print(f"   ❌ Utility Loss: '{text}' -> '{masked_text}' (Pred: {pred_masked})")

        print(f"   Original Accuracy: {original_score/len(dataset):.0%}")
        print(f"   Masked Accuracy:   {masked_score/len(dataset):.0%} (Should be close to Original)")

if __name__ == "__main__":
    print("🔬 STARTING SCIENTIFIC BENCHMARK")
    print("================================")
    
    # 1. Privacy
    priv_eval = PrivacyEvaluator()
    data = priv_eval.generate_labeled_data(200)
    priv_eval.evaluate(data)
    
    # 2. Utility
    util_eval = UtilityEvaluator()
    util_eval.run_benchmark()
