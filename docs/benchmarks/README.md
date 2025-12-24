# 🧪 Privalyse Mask Benchmarks

This directory contains experiments and benchmarks to validate the performance and utility of `privalyse-mask`.

## 1. Proxy Benchmarks (Fast & Local)
The script `comprehensive_benchmark.py` runs **Proxy Benchmarks**. 

### ❓ "How do we know utility without an LLM?"
We use **Heuristics** (Rules of Thumb) to estimate how useful the masked text will be to an LLM, without actually calling OpenAI/Anthropic APIs.

**The Logic:**
1. **Assumption**: An LLM needs specific "Context Tokens" to perform a task.
   - *Task*: "How old is the user?"
   - *Input*: "Born in 1990"
   - *Requirement*: The token `1990` must be present.
2. **Test**: We check if the *Masked Output* still contains these tokens.
   - *Masked*: `{Date_1990}` -> Contains `1990` -> **PASS** ✅
   - *Masked*: `{Date_REDACTED}` -> Missing `1990` -> **FAIL** ❌

### Advantages
- **Speed**: Runs in milliseconds.
- **Cost**: Free (no API tokens).
- **Determinism**: Results are 100% reproducible.

### Metrics
- **Consistency**: Can we `unmask()` the data back to the original?
- **Performance**: Characters processed per second.
- **Context Preservation**: Percentage of semantic tokens (Year, Month, Country) retained in surrogates.

---

## 2. Scientific Benchmark (Privacy & Utility)
The script `scientific_benchmark.py` provides a more rigorous evaluation framework.

### 🛡️ Privacy Evaluation (Recall)
- **Method**: Generates synthetic data with **known labels** using `Faker`.
- **Metric**: **Recall**.
  - Did we successfully mask the PII we injected?
  - `Recall = (Detected PII) / (Total Injected PII)`
- **Goal**: 100% Recall.

### 🤖 Utility Evaluation (Downstream Task)
- **Method**: Simulates an NLP task (Intent Classification) on both Original and Masked text.
- **Metric**: **Relative Accuracy**.
  - `Utility = (Accuracy on Masked) / (Accuracy on Original)`
- **Goal**: Utility should be close to 100% (Masking shouldn't break the model).

### How to run
```bash
python experiments/scientific_benchmark.py
```

## 3. LLM Evaluation (Slow & Expensive)
*Planned for future release.*

This involves sending the masked text to a real LLM (e.g., GPT-4) and grading the response.

**Workflow:**
1. Take a dataset of prompts (e.g., "Book a flight to Berlin").
2. Mask the PII: "Book a flight to {Location_Berlin}".
3. Send to LLM.
4. Check if LLM response is valid: "I have found flights to Berlin..."
5. Compare against response from unmasked text.

**Why not use this always?**
- Slow (network latency).
- Expensive (token costs).
- Flaky (LLMs are non-deterministic).
