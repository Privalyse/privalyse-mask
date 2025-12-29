![Privalyse Mask](https://privalyse.com/assets/github-privalyse-mask-readme-banner.png)

# 🛡️ privalyse-mask — Keep LLMs smart while keeping data private

[![PyPI version](https://img.shields.io/pypi/v/privalyse-mask.svg?color=green)](https://pypi.org/project/privalyse-mask/)
[![Downloads](https://pepy.tech/badge/privalyse-mask/month)](https://pepy.tech/project/privalyse-mask)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/Privalyse/privalyse-mask/actions/workflows/test.yml/badge.svg)](https://github.com/Privalyse/privalyse-mask/actions/workflows/test.yml)
[![Python Versions](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://pypi.org/project/privalyse-mask/)


A small open-source tool to **mask sensitive data** before sending it to LLMs — without destroying the context the model needs.

I built this because most masking tools turn your data into `[REDACTED]`.  
The problem? The LLM becomes blind and gives generic, useless answers.

**privalyse-mask** preserves semantic meaning:

| Input | Simple Redaction | privalyse-mask |
|-------|------------------|----------------|
| `Born on 12.10.2000` | `Born on [REDACTED]` | `Born on {Date_October_2000}` |
| `DE89 3704 0044...` | `[REDACTED]` | `{German_IBAN}` |
| `Peter` | `[REDACTED]` | `{Name_x92}` |

→ The LLM still knows the user is ~25 years old. But you never leaked their birthday.

---

## ⚡ Quick Start (3 lines)

```python
from privalyse_mask import PrivalyseMasker

masker = PrivalyseMasker()

# 1. Mask
masked, mapping = masker.mask("Peter was born on 12.10.2000, IBAN DE93...")
# → "{Name_x92} was born on {Date_October_2000}, IBAN {German_IBAN}"

# 2. Send to LLM (it sees structure, not secrets)
# response = llm.invoke(masked)

# 3. Unmask
final = masker.unmask(response, mapping)
```

![Privalyse Mask Demo](https://privalyse.com/assets/privalyse-mask-demo.gif)

---

## 🧠 Why Not Just Redact?

Most tools destroy the context LLMs need to give good answers:

```
Input:  "I was born on October 5, 2000 and live in Berlin"
Simple: "I was born on [REDACTED] and live in [REDACTED]"
        → LLM has no idea if user is 5 or 50, or what country they're in

Ours:   "I was born on {Date_October_2000} and live in Berlin"
        → LLM knows: ~25 years old, German timezone, German laws apply
```

**privalyse-mask** is the only open-source tool designed specifically to keep LLMs smart while keeping data private.

![Privalyse Mask Workflow](https://privalyse.com/assets/privalyse-mask-workflow.png)

---

## 🚀 Installation

```bash
pip install privalyse-mask
python -m spacy download en_core_web_lg
```

For other languages:
```bash
python -m spacy download de_core_news_lg  # German
python -m spacy download fr_core_news_lg  # French
python -m spacy download es_core_news_lg  # Spanish
```

---

## 🎯 Use Cases

- **RAG Pipelines** — Mask documents before vector indexing
- **Chatbots** — Consistent masking across conversation turns
- **LLM Testing** — Use realistic data without the risk
- **Tool Calling** — Keep function arguments private

---

## 🔌 Integrations

Works with any LLM provider. Examples included for:

| Provider | Example |
|----------|---------|
| OpenAI | [llm_example.py](examples/llm_example.py) |
| LangChain | [langchain_example.py](examples/providers/langchain_example.py) |
| Anthropic | [anthropic_example.py](examples/providers/anthropic_example.py) |
| Google Gemini | [gemini_example.py](examples/providers/gemini_example.py) |
| Ollama (Local) | [ollama_example.py](examples/providers/ollama_example.py) |
| Azure OpenAI | [azure_openai_example.py](examples/providers/azure_openai_example.py) |

### OpenAI Example

```python
from openai import OpenAI
from privalyse_mask import PrivalyseMasker

client = OpenAI()
masker = PrivalyseMasker()

# Mask before sending
prompt = "My email is alice@example.com and I was born on 15.03.1995"
masked_prompt, mapping = masker.mask(prompt)

# LLM sees: "My email is {Email_at_example.com} and I was born on {Date_March_1995}"
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": masked_prompt}]
)

# Restore PII in the response
final = masker.unmask(response.choices[0].message.content, mapping)
```

---

## 🧩 Features

| Feature | Description |
|---------|-------------|
| **Semantic Masking** | Preserves context (age, country, format) — not just `[REDACTED]` |
| **Reversible** | `unmask()` restores original values perfectly |
| **Multi-language** | EN, DE, FR, ES out of the box |
| **Async Support** | `mask_async()` for FastAPI, aiohttp, etc. |
| **Chat History** | `mask_struct()` keeps entity references consistent across messages |
| **Local & Stateless** | Your data never leaves your infrastructure |
| **Extensible** | Built on Microsoft Presidio + spaCy |

---

## 🛠️ Advanced Usage

### Mask Entire Conversations

For chat histories, use `mask_struct()` to keep entity references consistent:

```python
chat = [
    {"role": "user", "content": "My name is Peter"},
    {"role": "assistant", "content": "Hello Peter!"},
    {"role": "user", "content": "Peter needs help"}
]

masked_chat, mapping = masker.mask_struct(chat)
# All "Peter" instances → same "{Name_x92}" placeholder
```

### Async for Web Frameworks

```python
# FastAPI / aiohttp / async contexts
masked, mapping = await masker.mask_async(text)
restored = await masker.unmask_async(response, mapping)
```

### Multi-language

```python
masker = PrivalyseMasker(languages=["en", "de", "fr"])
```

---

## 📚 Documentation

| Guide | Description |
|-------|-------------|
| [Getting Started](docs/getting_started.md) | Installation & basic concepts |
| [Advanced Usage](docs/advanced_usage.md) | Custom rules, structure masking |
| [Integrations](docs/integrations.md) | LLM provider examples |
| [API Reference](docs/api.md) | Full method documentation |
| [Developer Guide](docs/developer_guide.md) | Architecture & contributing |

---

## 🗺️ Roadmap

- ✅ Multi-language support (EN, DE, FR, ES)
- ✅ Custom masking rules
- ✅ Async API for web frameworks
- ✅ Chat history masking (`mask_struct`)
- 🔜 Streaming support (critical for chatbots)
- 🔜 More entity types (crypto wallets, custom IDs)

---

## 💬 Feedback

This project is still early and evolving.

If you have ideas, notice edge cases, or use this in an interesting way — I'd genuinely love to hear about it.

- Open an [issue](https://github.com/Privalyse/privalyse-mask/issues)
- Start a [discussion](https://github.com/Privalyse/privalyse-mask/discussions)

---

## 📦 License

MIT License — see [LICENSE](LICENSE).
