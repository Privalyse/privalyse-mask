# 🛡️ Privalyse Mask Capabilities

This document outlines the current sanitization and masking capabilities of `privalyse-mask`.

## Supported Entities

The library currently supports detection and context-aware masking for the following entities:

| Entity Type | Description | Masking Strategy | Example Input | Example Output |
| :--- | :--- | :--- | :--- | :--- |
| **PERSON** | Names of people | `{Name_<Hash>}` | `Peter Parker` | `{Name_a1b2c}` |
| **DATE_TIME** | Dates and times | `{Date_<Month>_<Year>}` | `12.10.2000` | `{Date_October_2000}` |
| **IBAN_CODE** | Int. Bank Account Numbers | `{<Country>_IBAN}` | `DE93...` | `{German_IBAN}` |
| **DE_ID_CARD** | German ID Cards (Personalausweis) | `{German_ID}` | `T220001293` | `{German_ID}` |
| **EMAIL_ADDRESS** | Email addresses | `{Email}` | `peter@example.com` | `{Email}` |
| **PHONE_NUMBER** | Phone numbers | `{Phone}` | `+49 176 1234567` | `{Phone}` |
| **LOCATION** | Cities, Countries, etc. | `{Location_<Hash>}` | `Berlin` | `{Location_x9y8z}` |
| **PASSPORT** | Passport Numbers | `{<Country>_Passport}` | (Context dependent) | `{German_Passport}` |
| **DRIVER_LICENSE** | Driver Licenses | `{<Country>_Driver_License}` | (Context dependent) | `{US_Driver_License}` |

## Key Features

### 1. Context Preservation
Unlike simple redaction (e.g., `[REDACTED]`), our masks preserve:
- **Uniqueness**: Different people get different hashes (`{Name_A}` vs `{Name_B}`).
- **Semantics**: Dates retain Month/Year to allow LLMs to calculate approximate ages or timelines.
- **Origin**: IBANs and IDs retain their country of origin (e.g., `{German_IBAN}`).

### 2. Reversibility
Every `mask()` call returns a `mapping` dictionary. This dictionary is:
- **Ephemeral**: Created on the fly, not stored.
- **Secure**: Required to `unmask()` the LLM response.
- **Exact**: Ensures 1:1 restoration of the original data in the final output.

### 3. Extensibility
The system is built on **Microsoft Presidio** and **Spacy**, allowing for:
- Easy addition of new regex patterns (like the `GermanIDRecognizer`).
- Support for multiple languages (currently optimized for `en` and `de`).
