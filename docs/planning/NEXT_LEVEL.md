# 🚀 Next Level Features

Privalyse Mask goes beyond simple masking. We provide **context-aware pseudonymization** to maximize LLM utility.

## 1. Smart Address Masking (City Preservation)
We understand that "Location" is crucial context.
- **Cities/Countries**: Preserved. `Berlin` stays `Berlin`.
- **Specific Addresses**: Masked, but we try to preserve the city context if possible.
    - Input: `Musterstraße 5, Berlin`
    - Output: `{Address_in_Berlin}` (if detected as one entity) OR `{Address_Hash}, Berlin` (if detected separately).
    - **Benefit**: The LLM knows the jurisdiction and location, but not the house number.

## 2. Email Domain Preservation
- Input: `john.doe@company.com`
- Output: `{Email_at_company.com}`
- **Benefit**: Preserves B2B context. The LLM knows it's a corporate email vs. a personal one.

## 3. Phone Number Region
- Input: `+49 176 ...`
- Output: `{Phone_DE}`
- **Benefit**: Preserves the country context of the user.

## 4. Intelligent ID & IBAN Mapping
- **IBAN**: `{German_IBAN}`, `{French_IBAN}`.
- **IDs**: `{German_ID}`, `{US_Passport}`.
- **Benefit**: The LLM understands the *type* of document and its origin, allowing it to validate formats or ask relevant follow-up questions.

## 5. Structured Data Support (JSON/Agents)
Modern AI Agents communicate via JSON. Privalyse supports recursive masking of JSON structures.
- **Input**:
  ```json
  {
    "user": "Peter Parker",
    "email": "peter@techcorp.com"
  }
  ```
- **Output**:
  ```json
  {
    "user": "{Name_31c3b}",
    "email": "{Email_at_techcorp.com}"
  }
  ```
- **Benefit**: Perfect for RAG pipelines and Tool Calls.

## 6. Allow List
Define terms that should **never** be masked (e.g., your company name, project codes).
- `masker = PrivalyseMasker(allow_list=["TechCorp"])`
- Input: `TechCorp CEO Peter`
- Output: `TechCorp CEO {Name_...}`
