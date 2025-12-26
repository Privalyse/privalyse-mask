import sys
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# Add src to path if running from root without installing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from privalyse_mask import PrivalyseMasker

# Load environment variables
load_dotenv()

def main():
    print("☁️  Privalyse Mask - Azure OpenAI Example")
    print("========================================")

    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") # e.g. "gpt-4"

    if not api_key or not endpoint:
        print("❌ Error: AZURE_OPENAI_API_KEY or AZURE_OPENAI_ENDPOINT not found.")
        return

    client = AzureOpenAI(
        api_key=api_key,
        api_version="2024-02-15-preview",
        azure_endpoint=endpoint
    )
    
    masker = PrivalyseMasker(languages=["en"])

    # Sensitive input
    user_input = """
    Analyze the financial transaction for IBAN DE12 3456 7890 1234 5678 90.
    Account Holder: Max Mustermann.
    Amount: 50,000 EUR.
    """

    print(f"\n[Original Input]:\n{user_input}")

    # 1. Mask
    masked_text, mapping = masker.mask(user_input)
    print(f"\n[Masked Input]:\n{masked_text}")

    # 2. Call Azure OpenAI
    print("\n[Calling Azure OpenAI]...")
    try:
        response = client.chat.completions.create(
            model=deployment or "gpt-35-turbo", 
            messages=[
                {"role": "system", "content": "You are a financial analyst. Keep all placeholders like {German_IBAN} intact."},
                {"role": "user", "content": masked_text}
            ],
            temperature=0
        )
        
        llm_response = response.choices[0].message.content
        print(f"\n[LLM Response (Masked)]:\n{llm_response}")

        # 3. Unmask
        final_text = masker.unmask(llm_response, mapping)
        print(f"\n[Final Response (Unmasked)]:\n{final_text}")

    except Exception as e:
        print(f"Error calling Azure OpenAI: {e}")

if __name__ == "__main__":
    main()
