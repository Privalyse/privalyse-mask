# Advanced Usage

## Configuration

The `PrivalyseMasker` class offers several configuration options to tailor the masking process to your needs.

```python
from privalyse_mask import PrivalyseMasker

masker = PrivalyseMasker(
    languages=["en", "de"],      # Languages to support
    allow_list=["Privalyse"],    # Terms to NEVER mask
    seed="my-secret-project",    # Seed for consistent hashing
    model_size="lg"              # Spacy model size ("sm", "md", "lg")
)
```

### Parameters

-   **`languages`**: A list of language codes (e.g., `["en", "de", "es"]`). Ensure you have downloaded the corresponding Spacy models.
-   **`allow_list`**: A list of strings that should be ignored by the masker. Useful for company names or specific terminology.
-   **`seed`**: A string used to salt the hashes for surrogates (e.g., `{Name_x92}`). Using the same seed ensures that "Alice" always maps to the same placeholder across different runs, which is crucial for maintaining context in long conversations or databases.
-   **`model_size`**: The size of the Spacy model to use. Defaults to `"lg"` (large) for best accuracy.

## Structure Masking (JSON/Dicts)

When dealing with structured data (like API payloads or database records), you can use `mask_struct` to recursively mask strings within a dictionary or list while preserving the structure.

```python
data = {
    "user": {
        "name": "Alice Smith",
        "email": "alice@example.com"
    },
    "history": [
        "Login from Berlin",
        "Transaction: DE12 3456..."
    ]
}

masked_data, mapping = masker.mask_struct(data)

print(masked_data)
# Output:
# {
#     "user": {
#         "name": "{Name_a12}",
#         "email": "{Email_at_example.com}"
#     },
#     "history": [
#         "Login from {City_B}",
#         "Transaction: {German_IBAN}"
#     ]
# }
```

## Custom Recognizers

Privalyse Mask uses Microsoft Presidio under the hood. You can add custom recognizers to the underlying analyzer to detect domain-specific entities.

```python
from presidio_analyzer import Pattern, PatternRecognizer

# 1. Define a pattern (e.g., for a custom ID format)
sku_pattern = Pattern(name="sku_pattern", regex=r"\bSKU-\d{4}\b", score=0.8)
sku_recognizer = PatternRecognizer(supported_entity="PRODUCT_SKU", patterns=[sku_pattern])

# 2. Add to the masker's registry
masker.analyzer.registry.add_recognizer(sku_recognizer)

# 3. Mask
text = "Order for SKU-1234"
masked, mapping = masker.mask(text)
# Note: You may need to extend the surrogate generation logic if you want 
# specific formatting for new entity types. By default, it might use a generic fallback.
```

## Hashing & Consistency

The `seed` parameter is critical for consistency.

-   **Without Seed**: Hashes are random per instance. "Alice" might be `{Name_x92}` in one run and `{Name_b55}` in another.
-   **With Seed**: "Alice" will consistently map to `{Name_x92}`.

This is important for:
-   **Chat History**: Ensuring the LLM knows "Alice" is the same person mentioned earlier.
-   **Data Analysis**: Allowing you to join datasets on pseudonymized keys (if needed).
