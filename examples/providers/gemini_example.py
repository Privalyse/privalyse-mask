import sys
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Add src to path if running from root without installing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from privalyse_mask import PrivalyseMasker

# Load environment variables
load_dotenv()

def main():
    print("✨ Privalyse Mask - Google Gemini Example")
    print("========================================")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not found in .env file.")
        return

    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    masker = PrivalyseMasker(languages=["en"])

    # Sensitive input
    user_input = """
    Please write a recommendation letter for Peter Parker (born 2001-08-10).
    He lives at 20 Ingram St, New York.
    """

    print(f"\n[Original Input]:\n{user_input}")

    # 1. Mask
    masked_text, mapping = masker.mask(user_input)
    print(f"\n[Masked Input]:\n{masked_text}")

    # 2. Call Gemini
    print("\n[Calling Gemini]...")
    try:
        # Note: We can add a system instruction if using the system_instruction parameter in GenerativeModel
        # or just prepend it to the prompt.
        prompt = f"You are a helpful assistant. Keep the placeholders like {{Name_...}} exactly as they are.\n\n{masked_text}"
        
        response = model.generate_content(prompt)
        
        llm_response = response.text
        print(f"\n[LLM Response (Masked)]:\n{llm_response}")

        # 3. Unmask
        final_text = masker.unmask(llm_response, mapping)
        print(f"\n[Final Response (Unmasked)]:\n{final_text}")

    except Exception as e:
        print(f"Error calling Gemini: {e}")

if __name__ == "__main__":
    main()
