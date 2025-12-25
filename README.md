![Privalyse Mask](https://privalyse.com/assets/github-privalyse-mask-readme-banner.png)

# 🛡️ Privalyse Mask: Privacy Layer for LLMs & RAG

[![PyPI version](https://badge.fury.io/py/privalyse-mask.svg)](https://badge.fury.io/py/privalyse-mask)
[![Downloads](https://pepy.tech/badge/privalyse-mask/month)](https://pepy.tech/project/privalyse-mask)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/Privalyse/privalyse-mask/actions/workflows/test.yml/badge.svg)](https://github.com/Privalyse/privalyse-mask/actions/workflows/test.yml)
[![Python Versions](https://img.shields.io/pypi/pyversions/privalyse-mask.svg)](https://pypi.org/project/privalyse-mask/)

**Make your LLM & RAG pipelines privacy-aware in 3 lines of code.**

`privalyse-mask` is the middleware for privacy-first AI. It pseudonymizes sensitive data (PII) *before* it hits OpenAI, Anthropic, or your Vector DB, and restores it *after* the response—preserving full context for the model.

- **Peter** → `{Name_s73nd}` (Preserves entity type and uniqueness)
- **12.10.2000** → `{Date_October_2000}` (Preserves temporal context)
- **DE93...** → `{German_IBAN}` (Preserves financial context)

![Privalyse Mask Demo](https://privalyse.com/assets/privalyse-mask-demo.gif)

## ⚡ Quick Start

```python
from privalyse_mask import PrivalyseMasker

# 1. Mask PII (Peter -> {Name_x92}, Berlin -> {City_B})
masker = PrivalyseMasker()
safe_prompt, mapping = masker.mask("Peter lives in Berlin and uses IBAN DE12...")

# 2. Run LLM (The model sees structure, not secrets)
# ... llm.invoke(safe_prompt) ...

# 3. Unmask (Restore original data for the user)
final_response = masker.unmask(llm_response, mapping)
```

## 🎯 Why Privalyse Mask?

- **RAG & Chatbots**: Perfect for vector search and conversational AI.
- **Context-Aware**: Unlike `*****`, we preserve gender, nationality, and formats so the LLM stays smart.
- **Zero Leakage**: Your raw data never leaves your infrastructure.

```mermaid
flowchart LR
    A["User Input<br/>(PII)"] -->|Mask| B("Privalyse Mask")
    B -->|"Safe Prompt"| C["LLM"]
    C -->|"Safe Response"| D("Privalyse Unmask")
    D -->|"Final Response"| E["User"]
    style B fill:#e6f3ff,stroke:#2196f3,stroke-width:2px,color:#000
    style D fill:#e6f3ff,stroke:#2196f3,stroke-width:2px,color:#000
    style A fill:#fff,stroke:#333,color:#000
    style C fill:#fff,stroke:#333,color:#000
    style E fill:#fff,stroke:#333,color:#000
```

## 🚀 Installation

```bash
pip install privalyse-mask
python -m spacy download en_core_web_lg
```

## 🛠️ Usage

The core workflow is simple: `mask` the input, send to LLM, and `unmask` the response.

```python
from privalyse_mask import PrivalyseMasker

# Initialize the masker
masker = PrivalyseMasker()

# Your sensitive input
user_input = """
My name is Peter. I was born on 12.10.2000.
My IBAN is DE93 3432 2346 4355.
"""

# 1. Mask the data
masked_text, mapping = masker.mask(user_input)

print(f"Masked: {masked_text}")
# Output:
# "My name is {Name_s73nd}. I was born on {Date_October_2000}.
# My IBAN is {German_IBAN}."

# 2. Send to LLM (Simulation)
# llm_response = openai.ChatCompletion.create(..., messages=[{"role": "user", "content": masked_text}])
llm_response_text = f"Hello {masked_text.split()[3]}, I see your bank account is {masked_text.split()[-1]}."

# 3. Unmask the response
final_response = masker.unmask(llm_response_text, mapping)

print(f"Response: {final_response}")
# Output:
# "Hello Peter, I see your bank account is DE93 3432 2346 4355."
```

## 🔌 Integrations

### Using with OpenAI SDK

Protect your prompts before they leave your server.

```python
from openai import OpenAI
from privalyse_mask import PrivalyseMasker

client = OpenAI()
masker = PrivalyseMasker()

prompt = "My email is alice@example.com"
masked_prompt, mapping = masker.mask(prompt)

# Send safe prompt to OpenAI
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": masked_prompt}]
)

# Restore PII in the response
safe_response = masker.unmask(response.choices[0].message.content, mapping)
```

### Using with LangChain

Easily integrate into your chains.

```python
from langchain.prompts import PromptTemplate
from privalyse_mask import PrivalyseMasker

masker = PrivalyseMasker()

def safe_invoke(chain, input_text):
    masked_text, mapping = masker.mask(input_text)
    response = chain.invoke(masked_text)
    return masker.unmask(response, mapping)
```

### Secure Tool Calling

When LLMs call tools (e.g., database lookups), they will use the masked values (e.g., `{Name_x92}`). You must unmask these arguments before executing the tool.

See [examples/tool_calling_example.py](examples/tool_calling_example.py) for a full implementation pattern.

## 🧩 Features

- **Context-Aware Masking**: Dates are generalized to Month/Year. IDs are mapped to their type and origin.
- **Reversible**: A secure mapping object allows for perfect reconstruction of the LLM's response.
- **Stateless & Secure**: No data is stored persistently; mappings are ephemeral per request.
- **Extensible**: Built on top of Microsoft Presidio and Spacy.

## �️ Roadmap

We are building the standard for privacy-preserving AI.

- ✅ **Multi-language Support** (EN, DE supported, more coming)
- ✅ **Custom Masking Rules** (Add your own Regex/Logic)
- 🔄 **LangChain Integration Helper** (In Progress)
- 🔜 **Streaming Support** (Critical for Chatbots)
- 🔜 **PII-Presidio Adapter** (Easy migration)
## 🌟 Vision

We believe in maximizing the utility of LLMs without compromising user privacy. By mapping sensitive data to context-rich placeholders, we allow models to understand the *structure* and *nature* of the data without seeing the *actual* data.
## �📦 License

MIT License. See [LICENSE](LICENSE) for details.
## 👩‍💻 Developer Guide

### Architecture & Core Concepts
- **Entry Point**: `PrivalyseMasker` in [src/privalyse_mask/core.py](src/privalyse_mask/core.py) is the main class.
- **Analysis**: Uses `presidio-analyzer` to detect entities.
- **Custom Recognizers**: Extends Presidio with custom patterns (e.g., German ID, Spaced IBAN) in [src/privalyse_mask/recognizers.py](src/privalyse_mask/recognizers.py).
- **Masking Logic**:
  - **Surrogates**: Replaces entities with `{Type_Context}` or `{Type_Hash}` placeholders.
  - **Reversibility**: `mask()` returns a `mapping` dict (Surrogate → Original) to allow `unmask()` to restore the original text.
  - **Selective Masking**: Some entities (like generic Locations/Cities) are intentionally *not* masked (surrogate generator returns `None`) to preserve context.
- **Data Flow**: `Input Text` → `Analyzer` → `Entity Detection` → `Overlap Removal` → `Surrogate Generation` → `Replacement` → `Masked Text + Mapping`.

### Developer Workflow
- **Installation**:
  ```bash
  pip install -e .
  python -m spacy download en_core_web_lg  # Required for Presidio
  ```
- **Testing**:
  - Run tests with `pytest`.
  - Tests are located in [tests/](tests/).
- **Adding Recognizers**:
  1. Define `Pattern` and `PatternRecognizer` in [src/privalyse_mask/recognizers.py](src/privalyse_mask/recognizers.py).
  2. Register it in `PrivalyseMasker.__init__` in [src/privalyse_mask/core.py](src/privalyse_mask/core.py).

### Conventions & Patterns
- **Surrogate Format**: Always use curly braces `{...}`.
  - **Person**: `{Name_<hash>}`
  - **Date**: `{Date_<Month>_<Year>}` (via `dateparser`)
  - **IBAN**: `{<Country>_IBAN}`
  - **Email**: `{Email_at_<domain>}`
- **Hashing**: Use `utils.generate_hash_suffix` with the instance's `seed` for consistent but secure hashes.
- **Overlap Handling**: Custom greedy strategy in `_remove_overlaps` (Score > Length).
- **Structure Masking**: `mask_struct` handles recursive masking of JSON/Dict objects.

### Common Pitfalls
- **Spacy Model**: Ensure `en_core_web_lg` is installed; otherwise `AnalyzerEngine` initialization fails.
- **Presidio Overlaps**: Presidio often returns overlapping entities; `_remove_overlaps` is critical.
- **Date Parsing**: `dateparser` is used to extract semantic date info; fallback to `{Date_General}` if parsing fails.
