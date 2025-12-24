import sys
import os

# Add src to path if running from root without installing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from privalyse_mask import PrivalyseMasker

def main():
    print("🔒 Privalyse Mask - Mocked Example")
    print("==================================")

    # 1. Initialize
    # Ensure you have downloaded spacy models: python -m spacy download en_core_web_lg
    masker = PrivalyseMasker(languages=["en", "de"])

    # 2. Define sensitive input
    user_input = """
    Hello, my name is Sarah Connor. 
    I was born on 12.05.1984 in Los Angeles.
    I live at Evergreen Terrace 742, Springfield.
    My German bank account is DE93 1234 5678 9012 3456.
    My German ID card number is T220001293.
    You can reach me at sarah.connor@sky.net.
    """
    
    print(f"\n[Original Input]:\n{user_input}")

    # 3. Mask
    print("\n[Masking]...")
    masked_text, mapping = masker.mask(user_input)
    
    print(f"\n[Masked Input sent to LLM]:\n{masked_text}")
    print(f"\n[Mapping (Secret)]:\n{mapping}")

    # 4. Simulate LLM Response
    # The LLM sees the masked text and responds using the placeholders
    print("\n[Simulating LLM Response]...")
    
    # Let's pretend the LLM extracts the info and formats it
    # It sees: "Hello, my name is {Name_a1b2c}. I was born on {Date_May_1984}..."
    llm_response_mock = (
        f"Summary of user data:\n"
        f"- Name: {masked_text.split('name is ')[1].split('.')[0]}\n"
        f"- Birth Date: {masked_text.split('born on ')[1].split(' in')[0]}\n"
        f"- Location: {masked_text.split(' in ')[1].split('.')[0]}\n"
        f"- Address: {masked_text.split('live at ')[1].split('.')[0]}\n"
        f"- Financial: Found a {masked_text.split('account is ')[1].split('.')[0]}\n"
        f"- ID Document: {masked_text.split('number is ')[1].split('.')[0]}\n"
        f"- Contact: {masked_text.split('reach me at ')[1].split('.')[0]}"
    )
    
    print(f"\n[LLM Response (Masked)]:\n{llm_response_mock}")

    # 5. Unmask
    print("\n[Unmasking]...")
    final_response = masker.unmask(llm_response_mock, mapping)

    print(f"\n[Final Unmasked Response]:\n{final_response}")

if __name__ == "__main__":
    main()
