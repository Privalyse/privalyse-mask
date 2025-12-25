# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-12-25

### 🐛 Bug Fixes & Improvements
-   **Improved Recognition Accuracy**: Added a comprehensive stop-word filter for both German (e.g., "Ich") and English (e.g., "I", "They") to prevent pronouns from being misidentified as names.
-   **Better IBAN Detection**: Updated `SpacedIBANRecognizer` to handle IBANs with variable spacing and prevent truncation of the last digits.
-   **Date Merging**: Added logic to merge adjacent date entities (e.g., "October 5th, 2025") into a single semantic placeholder, improving LLM comprehension.
-   **Robust Initialization**: Fixed `AnalyzerEngine` initialization to correctly load language-specific Spacy models (e.g., `de_core_news_lg` for German) instead of defaulting to English.
-   **Recognizer Registration**: Custom recognizers are now correctly registered for all configured languages.

## [0.1.0] - 2025-12-23

### 🚀 Initial Release

We are proud to present the first public release of **Privalyse Mask**! 🛡️

This library solves the "Context vs. Privacy" dilemma for LLMs. Instead of destroying data with `<MASKED>` tags, we replace sensitive entities with **semantic surrogates** (e.g., `{Name_s73nd}`, `{Address_in_Berlin}`) to keep your AI smart while keeping your data safe.

#### ✨ Key Features
-   **Context-Aware Masking**: Preserves the semantic meaning of entities (e.g., distinguishing between a generic City and a specific Address).
-   **Reversibility**: Every `mask()` call returns a mapping to fully restore the original text.
-   **Multilingual**: Native support for 🇺🇸 English, 🇩🇪 German, 🇫🇷 French, 🇪🇸 Spanish, and 🇮🇹 Italian.
-   **Granular Config**: Toggle specific entities (e.g., mask Names but keep Dates) via `MaskingConfig`.
-   **Structure Support**: Recursively masks complex JSON/Dict objects with `mask_struct`.

#### 🛠️ Technical
-   Integration with Microsoft Presidio and Spacy.
-   Custom recognizers for German IDs and spaced IBANs.
-   Deterministic hashing for consistent pseudonymization across sessions.
