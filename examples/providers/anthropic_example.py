import sys
import os
from dotenv import load_dotenv
from anthropic import Anthropic

# Add src to path if running from root without installing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from privalyse_mask import PrivalyseMasker

# Load environment variables
load_dotenv()

def main():
    print("🤖 Privalyse Mask - Anthropic Claude Example")
    print("============================================")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY not found in .env file.")
        print("Please create a .env file with your API key.")
        return

    client = Anthropic(api_key=api_key)
    masker = PrivalyseMasker(languages=["en"])

    # Sensitive input
    user_input = """
    Draft a contract for Alice Wonderland (born 1990-05-12) 
    living at 123 Rabbit Hole Ln, London. 
    Her email is alice@wonderland.com.
    """

    print(f"\n[Original Input]:\n{user_input}")

    # 1. Mask
    masked_text, mapping = masker.mask(user_input)
    print(f"\n[Masked Input]:\n{masked_text}")

    # 2. Call Claude
    print("\n[Calling Claude]...")
    try:
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            temperature=0,
            system="You are a legal assistant. Use the provided placeholders (like {Name_...}) exactly as they appear in your response.",
            messages=[
                {"role": "user", "content": masked_text}
            ]
        )
        
        llm_response = message.content[0].text
        print(f"\n[LLM Response (Masked)]:\n{llm_response}")

        # 3. Unmask
        final_text = masker.unmask(llm_response, mapping)
        print(f"\n[Final Response (Unmasked)]:\n{final_text}")

    except Exception as e:
        print(f"Error calling Anthropic: {e}")

if __name__ == "__main__":
    main()
