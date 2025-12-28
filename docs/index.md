# 🛡️ Privalyse Mask Documentation

Welcome to the documentation for **Privalyse Mask**, the privacy layer for LLMs and RAG pipelines.

## Overview

`privalyse-mask` is a Python library designed to pseudonymize sensitive data (PII) in text before it is processed by Large Language Models (LLMs) or stored in vector databases. It ensures privacy compliance (GDPR, CCPA) while preserving the semantic context necessary for high-quality AI responses.

### Key Features

-   **Context-Aware Masking**: Replaces PII with semantic placeholders (e.g., `Peter` -> `{Name_s73nd}`, `Berlin` -> `{City_B}`) rather than generic tokens like `*****` or `<PERSON>`.
-   **Reversible**: Provides a mapping to restore the original data in the LLM's response.
-   **Customizable**: Supports custom recognizers, allow-lists, and multiple languages.
-   **Easy Integration**: Designed to fit seamlessly into existing Python workflows, RAG pipelines, and chatbot frameworks.

## Navigation

-   [**Getting Started**](getting_started.md): Installation and your first masking example.
-   [**Advanced Usage**](advanced_usage.md): Configuration options, custom recognizers, and structure masking.
-   [**Integrations**](integrations.md): Guides for using Privalyse Mask with OpenAI, LangChain, and RAG pipelines.
-   [**API Reference**](api.md): Detailed documentation of the `PrivalyseMasker` class and its methods.
-   [**Benchmarks**](benchmarks/README.md): Performance and accuracy benchmarks.

## Quick Example

```python
from privalyse_mask import PrivalyseMasker

# Initialize
masker = PrivalyseMasker()

# Mask
text = "Contact Peter at peter@example.com"
masked_text, mapping = masker.mask(text)

print(masked_text)
# Output: "Contact {Name_x92} at {Email_at_example.com}"

# Unmask
original_text = masker.unmask(masked_text, mapping)
```
