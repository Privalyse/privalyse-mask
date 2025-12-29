# API Reference

## `PrivalyseMasker`

The main class for handling PII masking and unmasking.

```python
from privalyse_mask import PrivalyseMasker
```

### `__init__`

```python
def __init__(self, 
             languages: List[str] = ["en", "de"], 
             allow_list: List[str] = [], 
             seed: str = "", 
             model_size: str = "lg")
```

Initializes the masker with specified languages and configuration.

-   **`languages`** (`List[str]`): List of ISO language codes to support. Default is `["en", "de"]`. Requires corresponding Spacy models to be installed.
-   **`allow_list`** (`List[str]`): List of terms that should be excluded from masking. Case-insensitive.
-   **`seed`** (`str`): A string used to salt the hashes for surrogates. Ensures deterministic masking (e.g., same name -> same hash) across instances if the same seed is used.
-   **`model_size`** (`str`): Spacy model size suffix (`"sm"`, `"md"`, `"lg"`). Default is `"lg"`.

### `mask`

```python
def mask(self, text: str, language: str = "en") -> Tuple[str, Dict[str, str]]
```

Analyzes the text for PII and replaces it with surrogates.

-   **`text`** (`str`): The input text to mask.
-   **`language`** (`str`): The language code of the text (default `"en"`). Used to select the correct analyzer model.

**Returns**:
-   A tuple `(masked_text, mapping)`.
    -   `masked_text` (`str`): The text with PII replaced by placeholders.
    -   `mapping` (`Dict[str, str]`): A dictionary mapping surrogates (keys) back to original values (values).

### `mask_struct`

```python
def mask_struct(self, data: Any, language: str = "en") -> Tuple[Any, Dict[str, str]]
```

Recursively masks PII in a structured object (JSON-like).

-   **`data`** (`Any`): The input structure (dict, list, string, etc.).
-   **`language`** (`str`): The language code.

**Returns**:
-   A tuple `(masked_data, mapping)`.
    -   `masked_data`: The structure with all string values masked.
    -   `mapping`: A combined mapping dictionary for all masked strings.

### `unmask`

```python
def unmask(self, text: str, mapping: Dict[str, str]) -> str
```

Restores the original PII in the text using the provided mapping.

-   **`text`** (`str`): The text containing surrogates (usually the LLM response).
-   **`mapping`** (`Dict[str, str]`): The mapping dictionary returned by `mask()` or `mask_struct()`.

**Returns**:
-   `str`: The text with surrogates replaced by their original values.

---

## Async Methods

For async web frameworks (FastAPI, aiohttp, Starlette), use these non-blocking variants. They run the CPU-bound Presidio analysis in a thread pool via `asyncio.run_in_executor()`.

### `mask_async`

```python
async def mask_async(self, text: str, language: str = "en") -> Tuple[str, Dict[str, str]]
```

Async version of `mask()`. Same parameters and return values.

### `mask_struct_async`

```python
async def mask_struct_async(self, data: Any, language: str = "en") -> Tuple[Any, Dict[str, str]]
```

Async version of `mask_struct()`. Ideal for masking entire chat histories without blocking.

### `unmask_async`

```python
async def unmask_async(self, masked_text: str, mapping: Dict[str, str]) -> str
```

Async version of `unmask()`. Keeps API symmetry for fully async codebases.

**Example (FastAPI)**:

```python
from fastapi import FastAPI
from privalyse_mask import PrivalyseMasker

app = FastAPI()
masker = PrivalyseMasker()

@app.post("/chat")
async def chat(user_message: str):
    masked, mapping = await masker.mask_async(user_message)
    llm_response = await call_llm(masked)  # Your LLM call
    return await masker.unmask_async(llm_response, mapping)
```
