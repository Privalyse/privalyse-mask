# Contributing to Privalyse Mask

First off, thanks for taking the time to contribute! 🎉

The following is a set of guidelines for contributing to `privalyse-mask`. These are mostly guidelines, not rules. Use your best judgment and feel free to propose changes to this document in a pull request.

## 🛠️ Development Setup

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/privalyse-mask.git
    cd privalyse-mask
    ```

2.  **Create a virtual environment**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies**
    We use `pip` with editable mode for development:
    ```bash
    pip install -e .
    pip install pytest  # For running tests
    ```

4.  **Download Spacy Models**
    Privalyse Mask requires the large English model by default:
    ```bash
    python -m spacy download en_core_web_lg
    ```

## 🧪 Running Tests

We use `pytest` for testing. Ensure all tests pass before submitting a PR.

```bash
pytest
```

To run a specific test file:
```bash
pytest tests/test_core.py
```

## 🧩 Adding New Recognizers

If you want to add support for a new PII type (e.g., a specific ID card format):

1.  Open `src/privalyse_mask/recognizers.py`.
2.  Create a new function that returns a `PatternRecognizer`.
3.  Register it in `PrivalyseMasker.__init__` in `src/privalyse_mask/core.py`.
4.  Add a test case in `tests/test_core.py`.

## 📝 Style Guide

-   **Code**: We follow standard PEP 8 guidelines.
-   **Commits**: Please write clear commit messages (e.g., `feat: add German IBAN support` or `fix: handle null values in date parser`).

## 🐛 Reporting Bugs

Bugs are tracked as GitHub issues. When filing an issue, please include:
-   A clear title and description.
-   A code snippet to reproduce the issue.
-   The version of `privalyse-mask` you are using.
