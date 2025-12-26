import sys
import os
from dotenv import load_dotenv
from groq import Groq

# Add src to path if running from root without installing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from privalyse_mask import PrivalyseMasker

# Load environment variables
load_dotenv()

def main():
    print("⚡ Privalyse Mask - Groq (Llama 3) Example")
    print("==========================================")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ Error: GROQ_API_KEY not found in .env file.")
        return

    client = Groq(api_key=api_key)
    masker = PrivalyseMasker(languages=["en"])

    # Sensitive input
    user_input = """
    Extract the key entities from this text:
    "Meeting with Sarah Connor at Cyberdyne Systems on August 29th, 1997."
    """

    print(f"\n[Original Input]:\n{user_input}")

    # 1. Mask
    masked_text, mapping = masker.mask(user_input)
    print(f"\n[Masked Input]:\n{masked_text}")

    # 2. Call Groq
    print("\n[Calling Groq (Llama 3)]...")
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an entity extractor. Return the entities found in the text, keeping the placeholders (e.g. {Name_...}) exactly as they are."},
                {"role": "user", "content": masked_text}
            ],
            model="llama3-8b-8192",
        )
        
        llm_response = chat_completion.choices[0].message.content
        print(f"\n[LLM Response (Masked)]:\n{llm_response}")

        # 3. Unmask
        final_text = masker.unmask(llm_response, mapping)
        print(f"\n[Final Response (Unmasked)]:\n{final_text}")

    except Exception as e:
        print(f"Error calling Groq: {e}")

if __name__ == "__main__":
    main()
