![Privalyse Mask](https://privalyse.com/assets/github-privalyse-mask-readme-banner.png)

# 🛡️ privalyse-mask — Mask sensitive data before sending it to LLMs

A small open-source tool to mask sensitive data before sending it to LLMs.

I built this because I kept running into the same problem:
I wanted to experiment with LLMs without accidentally leaking real user data.

This project is intentionally simple.  
It’s meant to be useful, not magical — and it’s still evolving.

---

## ⚡ Quick example
Here’s what using it looks like in practice:

```python
from privalyse_mask import PrivalyseMasker

masker = PrivalyseMasker()

text = "Peter lives in Berlin and his IBAN is DE93..."
masked, mapping = masker.mask(text)

# -> "Peter" becomes "{Name_x92}"
# -> "DE93..." becomes "{German_IBAN}"
```

Send the masked text to your LLM, then restore it afterwards:

```python
final = masker.unmask(llm_response, mapping)
```

---

## 🤔 What this does

* Masks sensitive data before it leaves your system
* Preserves structure so prompts still work
* Restores the original values after the LLM response

This makes it easier to experiment with LLMs without exposing real user data.

---

## 🧩 When this is useful

* Prototyping LLM features
* RAG pipelines
* Chatbots and assistants
* Testing with realistic input

---

## ⚠️ When this is probably not the right tool

* Large-scale anonymization pipelines
* Compliance-heavy production environments
* Full data governance systems

(This project intentionally stays lightweight.)

---

## 🖼️ Example

![Privalyse Mask Demo](https://privalyse.com/assets/privalyse-mask-demo.gif)

---

## 🚀 Installation

```bash
pip install privalyse-mask
python -m spacy download en_core_web_lg
```

---

## 🛠️ Basic usage

```python
from privalyse_mask import PrivalyseMasker

masker = PrivalyseMasker()

user_input = """
My name is Peter. I was born on 12.10.2000.
My IBAN is DE93 3432 2346 4355.
"""

masked_text, mapping = masker.mask(user_input)

# Send masked_text to your LLM...

final_response = masker.unmask(llm_response, mapping)
```

---

## 🔌 Integrations

Examples are available for:

* OpenAI
* LangChain
* Anthropic
* Google Gemini
* Ollama (local LLMs)
* Hugging Face

See: [`docs/integrations.md`](docs/integrations.md)

---

## 🧩 Features

* **Context-aware masking**
  (Dates, IDs, names keep semantic meaning)

* **Reversible**
  (Original values can be restored safely)

* **Stateless**
  (No data is stored between calls)

* **Extensible**
  (Built on Presidio + spaCy)

* **Async support**
  (Non-blocking for FastAPI, aiohttp, etc.)

---

## 🗺️ Roadmap

* ✅ Multi-language support (EN, DE, FR, ES)
* ✅ Custom masking rules
* ✅ Async API for web frameworks
* 🔄 Helper utilities for LLM frameworks
* 🔜 Streaming support (for chat use cases)

---

## 💬 Feedback & contributions

This project is still evolving.

If you:

* have ideas
* notice missing features
* or use this in an interesting way

I’d genuinely love to hear about it — whether it’s feedback, ideas, or how you’re using it.

---

## 📚 Documentation

* [Getting Started](docs/getting_started.md)
* [Advanced Usage](docs/advanced_usage.md)
* [Integrations](docs/integrations.md)
* [API Reference](docs/api.md)
* [Developer Guide](docs/developer_guide.md)

---

## 📦 License

MIT License — see [LICENSE](LICENSE).
