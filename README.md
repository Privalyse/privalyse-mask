# 🛡️ Privalyse Mask

### **Redefining Privacy in AI-Applications.**
#### *The Privacy-Protection Layer for your LLM Pipeline.*

[![PyPI version](https://badge.fury.io/py/privalyse-mask.svg)](https://badge.fury.io/py/privalyse-mask)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## 💥 Stop choosing between Privacy and High-Quality Answers.

**Privalyse Mask** is the missing link that makes LLMs GDPR-compliant **without making them stupid.**

Most tools destroy data to save it. We don't.
We transform sensitive PII into **Semantic Surrogates**—tokens that preserve gender, culture, geography, and structure—so your AI still "gets it" while the data stays safe.

**Zero Leaks. Full Context. 100% Reversible.**

> ⭐ **Star this repository if you believe in Privacy-First AI!**

---

## 🧠 The Dilemma: Utility vs. Privacy
When sending data to an LLM, you usually have two bad options:
1.  **Send Everything**: You risk GDPR fines and data leaks.
2.  **Redact Everything**: The LLM becomes stupid. "John from Berlin" becomes `[PERSON] from [LOCATION]`. The model loses gender, culture, and geography.

## 💡 The Solution: Semantic Masking
**Privalyse Mask** solves this by replacing sensitive entities with **Context-Aware, Reversible Surrogates**. We preserve the *meaning* while hiding the *identity*.

| Original Input | Standard Redaction | Privalyse Mask |
| :--- | :--- | :--- |
| *"John Smith lives at 123 Main St, New York."* | `[PERSON] lives at [ADDRESS].` | `"{User_61173_Prename_John} lives at {Address_in_New York_Street_cb7e6}."` |
| *"Max Mustermann wohnt in Berlin."* | `[PERSON] wohnt in [LOCATION].` | `"{User_44aa4_Prename_Max} wohnt in {Address_in_Berlin}."` |
| *"Call me at +49 30 123456."* | `Call me at [PHONE].` | `Call me at {Phone_DE}.` |

✅ **The Model Understands:** "This is a male person named John living in NYC."
❌ **The Model Doesn't Know:** Who exactly it is or where exactly they live.

---

## ⚡ Usage in 3 Lines

```python
from privalyse_mask import PrivalyseMasker

# Automatically loads EN, DE, FR, ES, IT models
masker = PrivalyseMasker() 

masked_text, mapping = masker.mask("John lives in Berlin.")
# Result: "{User_a1b2_Prename_John} lives in {Address_in_Berlin}."
```

---

## ✨ Why Privalyse Mask?

### 1. 🌍 True Multilingual Support
We don't just support English. We have native, fine-tuned recognition for:
*   🇺🇸 **English** (US/UK)
*   🇩🇪 **German** (DACH)
*   🇫🇷 **French**
*   🇪🇸 **Spanish**
*   🇮🇹 **Italian**

### 2. 🎭 Granular Control
Decide exactly how much context you want to reveal.
*   **`MASK_ALL`**: `{PERSON}` (Maximum Privacy)
*   **`PARTIAL_MASK`**: `{User_Hash_Prename_John}` (Maximum Utility)
*   **`KEEP_VISIBLE`**: `Berlin` (Keep Cities visible for context)

### 3. 🔄 100% Reversible & Consistent
Every masking operation generates a secure, ephemeral mapping. You can perfectly reconstruct the LLM's response.
*   **Input**: "Hello `{User_a1b2_Prename_John}`..."
*   **Output**: "Hello John..."

By using a **Seed**, you ensure that "John" is always masked to the same ID across different sessions or chat messages.

### 4. 🆔 Specialized Recognizers
We go beyond standard NER. We detect:
*   **German IBANs** (even with spaces)
*   **German IDs** (Personalausweis)
*   **Complex Addresses** (Street vs. City separation)

---

## 🚀 Installation

```bash
pip install privalyse-mask
```

*Note: You will need to download the Spacy models for your desired languages (e.g., `python -m spacy download en_core_web_lg`).*

---

## 🛠️ Advanced Configuration

```python
from privalyse_mask import PrivalyseMasker, MaskingConfig, MaskingLevel

# Configure masking granularity
config = MaskingConfig(
    default_level=MaskingLevel.PARTIAL_MASK, # Default: {User_Hash_Prename_John}
    entity_overrides={
        "LOCATION": MaskingLevel.KEEP_VISIBLE,   # Keep cities like "Paris" visible
        "PHONE_NUMBER": MaskingLevel.MASK_ALL,   # Just {PHONE_NUMBER}
        "EMAIL_ADDRESS": MaskingLevel.MASK_WITH_CONTEXT # {Email_at_gmail.com}
    }
)

masker = PrivalyseMasker(config=config)
```

### 📂 Handling JSON & Chat History
You can mask entire JSON objects (e.g., chat history) recursively.

```python
chat_history = [
    {"role": "user", "content": "My name is John."},
    {"role": "assistant", "content": "Hello John!"}
]

# mask_struct handles Dicts and Lists recursively
masked_history, mapping = masker.mask_struct(chat_history)
```

---

## 🚀 The Vision: The Privacy Hub for AI

We are building the central nervous system for secure AI development.

*   **[Privalyse CLI](https://github.com/privalyse/privalyse-cli)**: **The Eyes (Visibility & Detection)**.
    *   Illuminates the black box.
    *   Scans your codebase and runtime for vulnerabilities.
    *   Detects leaks *before* they happen.

*   **Privalyse Mask**: **The Shield (Proactive Protection)**.
    *   Safeguards data in real-time.
    *   Ensures compliance by design.
    *   Preserves utility through semantic masking.

**Don't just find leaks. Prevent them.**

---

## 🌐 The Privalyse Ecosystem

We are creating a unified ecosystem where privacy is a catalyst for better AI.

*   **[Privalyse.com](https://privalyse.com)**: Our Vision & Platform.
*   **[Privalyse CLI](https://github.com/privalyse/privalyse-cli)**: Scan your codebase.
*   **Privalyse Mask**: Protect your pipeline.

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
