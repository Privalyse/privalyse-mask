# 👩‍💻 Developer Guide

## Architecture & Core Concepts
- **Entry Point**: `PrivalyseMasker` in [src/privalyse_mask/core.py](../src/privalyse_mask/core.py) is the main class.
- **Analysis**: Uses `presidio-analyzer` to detect entities.
- **Custom Recognizers**: Extends Presidio with custom patterns (e.g., German ID, Spaced IBAN) in [src/privalyse_mask/recognizers.py](../src/privalyse_mask/recognizers.py).
- **Masking Logic**:
  - **Surrogates**: Replaces entities with `{Type_Context}` or `{Type_Hash}` placeholders.
  - **Reversibility**: `mask()` returns a `mapping` dict (Surrogate → Original) to allow `unmask()` to restore the original text.
  - **Selective Masking**: Some entities (like generic Locations/Cities) are intentionally *not* masked (surrogate generator returns `None`) to preserve context.
- **Data Flow**: `Input Text` → `Analyzer` → `Entity Detection` → `Overlap Removal` → `Surrogate Generation` → `Replacement` → `Masked Text + Mapping`.

## Developer Workflow
- **Installation**:
  ```bash
  pip install -e .
  python -m spacy download en_core_web_lg  # Required for Presidio
  ```
- **Testing**:
  - Run tests with `pytest`.
  - Tests are located in [tests/](../tests/).
- **Adding Recognizers**:
  1. Define `Pattern` and `PatternRecognizer` in [src/privalyse_mask/recognizers.py](../src/privalyse_mask/recognizers.py).
  2. Register it in `PrivalyseMasker.__init__` in [src/privalyse_mask/core.py](../src/privalyse_mask/core.py).

## Conventions & Patterns
- **Surrogate Format**: Always use curly braces `{...}`.
  - **Person**: `{Name_<hash>}`
  - **Date**: `{Date_<Month>_<Year>}` (via `dateparser`)
  - **IBAN**: `{<Country>_IBAN}`
  - **Email**: `{Email_at_<domain>}`
- **Hashing**: Use `utils.generate_hash_suffix` with the instance's `seed` for consistent but secure hashes.
- **Overlap Handling**: Custom greedy strategy in `_remove_overlaps` (Score > Length).
- **Structure Masking**: `mask_struct` handles recursive masking of JSON/Dict objects.

## Common Pitfalls
- **Spacy Model**: Ensure `en_core_web_lg` is installed; otherwise `AnalyzerEngine` initialization fails.
- **Presidio Overlaps**: Presidio often returns overlapping entities; `_remove_overlaps` is critical.
- **Date Parsing**: `dateparser` is used to extract semantic date info; fallback to `{Date_General}` if parsing fails.
