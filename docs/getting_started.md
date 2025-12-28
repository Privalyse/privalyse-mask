# Getting Started

## Installation

### Prerequisites

-   Python 3.8 or higher
-   pip

### Install Package

Install `privalyse-mask` via pip:

```bash
pip install privalyse-mask
```

### Download Language Models

Privalyse Mask relies on `spacy` models for Named Entity Recognition (NER). You must download the appropriate model for the languages you intend to use.

For **English** (default):

```bash
python -m spacy download en_core_web_lg
```

For **German**:

```bash
python -m spacy download de_core_news_lg
```

> **Note**: We recommend the `lg` (large) models for better accuracy, but `md` (medium) or `sm` (small) can be used for faster performance with reduced accuracy.

## Basic Usage

The core workflow involves three steps:
1.  **Masking**: Convert sensitive text into a safe, pseudonymized format.
2.  **Processing**: Send the masked text to your LLM or database.
3.  **Unmasking**: Restore the original entities in the response.

### 1. Initialize the Masker

```python
from privalyse_mask import PrivalyseMasker

# Initialize with default settings (English & German support)
masker = PrivalyseMasker()
```

### 2. Masking Text

Use the `mask()` method to process text. It returns the masked string and a `mapping` dictionary required for reversal.

```python
user_input = "My name is Alice and I live in London."

masked_text, mapping = masker.mask(user_input)

print(f"Masked: {masked_text}")
# Output: "My name is {Name_a12}. I live in {City_L}."

print(f"Mapping: {mapping}")
# Output: {'{Name_a12}': 'Alice', '{City_L}': 'London'}
```

### 3. Unmasking

After processing the masked text (e.g., getting a response from an LLM), use `unmask()` to restore the original values.

```python
# Simulate an LLM response using the masked entities
llm_response = "Hello {Name_a12}, how is the weather in {City_L}?"

final_response = masker.unmask(llm_response, mapping)

print(f"Restored: {final_response}")
# Output: "Hello Alice, how is the weather in London?"
```

## Next Steps

-   Learn about [Advanced Configuration](advanced_usage.md) to customize languages and recognizers.
-   See [Integrations](integrations.md) for using Privalyse Mask with OpenAI and LangChain.
