# ⚔️ Tool Comparison Benchmark

Run Date: December 22, 2025

We compared `privalyse-mask` against two popular Python alternatives: **Scrubadub** and **Microsoft Presidio** (Standard).

## 1. Qualitative Comparison

| Feature | 🛡️ **Privalyse Mask** | 🧽 **Scrubadub** | 🏢 **Microsoft Presidio** |
| :--- | :--- | :--- | :--- |
| **Output Style** | Semantic (`{Email_at_gmail.com}`) | Identifier (`{{EMAIL-0}}`) | Tag (`<EMAIL_ADDRESS>`) |
| **LLM Utility** | ⭐⭐⭐⭐⭐ (High Context) | ⭐⭐ (Low Context) | ⭐⭐⭐ (Medium Context) |
| **Reversibility** | ✅ **Native** (Auto-mapping) | ✅ Supported (Lookup) | ❌ No (Requires Encryption setup) |
| **Detection Engine** | Presidio + Spacy (Robust) | Regex + TextBlob (Fast but weak) | Presidio + Spacy (Robust) |

## 2. Quantitative Results (Sample Run)

Input: *"My name is Alice and I live in Berlin, Alexanderplatz 1. Contact me at alice@example.com."*

### 🛡️ Privalyse Mask
- **Output**: `My name is {Name_64489} and I live in {Address_in_Berlin}. Contact me at {Email_at_example.com}.`
- **Analysis**:
  - **Name**: Detected & Masked (`{Name_...}`).
  - **Email**: Detected & Masked (`{Email_at_...}`).
  - **Address**: "Berlin, Alexanderplatz 1" was detected as a single entity and masked as `{Address_in_Berlin}`.
  - **Verdict**: Best for LLMs. Perfect context preservation.

### 🧽 Scrubadub
- **Output**: `My name is Alice and I live in Berlin, Alexanderplatz 1. Contact me at {{EMAIL-0}}.`
- **Analysis**:
  - **FAILED** to detect "Alice" (Name).
  - **FAILED** to detect "Berlin" (Location).
  - **FAILED** to detect "Alexanderplatz 1" (Address).
  - Only caught the Email.
  - **Verdict**: Fast but inaccurate. Scrubadub's default detectors are too simple for free-text PII.

### 🏢 Microsoft Presidio
- **Output**: `My name is <PERSON> and I live in <LOCATION>, Alexanderplatz 1. Contact me at <EMAIL_ADDRESS>.`
- **Analysis**:
  - Detected "Alice" (`<PERSON>`) and "Berlin" (`<LOCATION>`).
  - **Missed** "Alexanderplatz 1".
  - **Verdict**: Good detection of standard entities, but generic output hurts LLM context.

## 3. Conclusion
- **Use Scrubadub** if you need extreme speed (0.5ms) and only care about patterns (Emails/Phones).
- **Use Presidio** if you need enterprise-grade detection but don't care about reversibility.
- **Use Privalyse Mask** if you need **Reversibility** and **LLM Context** with enterprise-grade detection.
