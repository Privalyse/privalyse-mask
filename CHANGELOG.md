# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-12-23

### 🚀 Initial Release
-   **Core**: `PrivalyseMasker` class for context-aware PII pseudonymization.
-   **Masking**: Support for Names, Emails, IBANs, Phone Numbers, and Dates.
-   **Semantic Surrogates**: Replaces PII with meaningful placeholders (e.g., `{Name_s73nd}`, `{Address_in_Berlin}`).
-   **Reversibility**: `mask()` returns a mapping dictionary to restore original data.
-   **Multilingual**: Native support for English, German, French, Spanish, and Italian via Spacy.
-   **Configuration**: Granular control via `MaskingConfig` (toggle specific entity types).
-   **Structure Support**: Recursive masking for JSON/Dict objects via `mask_struct`.

### 🛠️ Technical
-   Integration with Microsoft Presidio and Spacy.
-   Custom recognizers for German IDs and spaced IBANs.
-   Deterministic hashing for consistent pseudonymization across sessions.
