from privalyse_mask import PrivalyseMasker, MaskingConfig, MaskingLevel

def main():
    # 1. Define a custom configuration
    # We want to:
    # - Keep Cities visible (e.g. "Berlin") to preserve location context
    # - Mask Phone numbers completely (no context)
    # - Mask Names with partial context (First Name + Hash)
    config = MaskingConfig(
        default_level=MaskingLevel.PARTIAL_MASK, # Default behavior
        entity_overrides={
            "LOCATION": MaskingLevel.KEEP_VISIBLE,
            "PHONE_NUMBER": MaskingLevel.MASK_ALL
        }
    )

    # 2. Initialize Masker with Config (defaults to all languages)
    masker = PrivalyseMasker(config=config)

    # 3. Input Text
    text = """
    Hello, my name is Alice Wonderland. I live in London.
    You can reach me at +44 20 7946 0958.
    """

    print(f"Original:\n{text}\n")

    # 4. Mask
    masked_text, mapping = masker.mask(text)

    print(f"Masked:\n{masked_text}\n")
    # Expected: 
    # Hello, my name is {User_..._Prename_Alice}. I live in London.
    # You can reach me at {PHONE_NUMBER}.

    # 5. Unmask
    restored_text = masker.unmask(masked_text, mapping)
    print(f"Restored:\n{restored_text}")

if __name__ == "__main__":
    main()
