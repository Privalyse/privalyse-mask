import sys
import os
import time
import scrubadub
from scrubadub.utils import Lookup
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_analyzer import AnalyzerEngine

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from privalyse_mask import PrivalyseMasker

class ToolBenchmark:
    def __init__(self):
        print("🔧 Initializing Tools...")
        # 1. Privalyse Mask
        self.privalyse = PrivalyseMasker(languages=["en"])
        
        # 2. Scrubadub
        self.scrubber = scrubadub.Scrubber()
        # Note: Scrubadub uses 'detectors' added by default
        
        # 3. Presidio (Raw)
        self.presidio_analyzer = AnalyzerEngine()
        self.presidio_anonymizer = AnonymizerEngine()

    def run_comparison(self):
        print("\n⚔️  Running Tool Comparison Benchmark...")
        
        # Updated text with Street Address as requested
        text = "My name is Alice and I live in Berlin, Alexanderplatz 1. Contact me at alice@example.com."
        print(f"Input: '{text}'\n")

        # --- 1. Privalyse Mask ---
        start = time.time()
        priv_masked, priv_map = self.privalyse.mask(text)
        priv_time = (time.time() - start) * 1000
        
        print(f"🛡️  Privalyse Mask ({priv_time:.2f}ms)")
        print(f"   Output: {priv_masked}")
        print(f"   Reversible: ✅ (Map size: {len(priv_map)})")
        print(f"   Context: {'✅' if 'Berlin' in priv_masked or 'Location' in priv_masked else '❌'}")

        # --- 2. Scrubadub ---
        start = time.time()
        # To make it reversible, we need a Lookup
        lookup = Lookup()
        scrub_masked = scrubadub.clean(text, replace_with='identifier', lookup=lookup)
        scrub_time = (time.time() - start) * 1000
        
        print(f"\n🧽 Scrubadub ({scrub_time:.2f}ms)")
        print(f"   Output: {scrub_masked}")
        print(f"   Reversible: ✅ (Lookup used)")
        # Scrubadub usually replaces with {{NAME-0}}, so context is lost
        print(f"   Context: {'✅' if 'Berlin' in scrub_masked else '❌'} (Generic tags)")

        # --- 3. Presidio (Raw) ---
        start = time.time()
        results = self.presidio_analyzer.analyze(text=text, language="en")
        presidio_masked = self.presidio_anonymizer.anonymize(
            text=text,
            analyzer_results=results
        ).text
        presidio_time = (time.time() - start) * 1000
        
        print(f"\n🏢 Microsoft Presidio ({presidio_time:.2f}ms)")
        print(f"   Output: {presidio_masked}")
        print(f"   Reversible: ❌ (Default is redaction)")
        print(f"   Context: {'✅' if 'Berlin' in presidio_masked else '⚠️'} (Generic tags <LOCATION>)")

if __name__ == "__main__":
    bench = ToolBenchmark()
    bench.run_comparison()
