import sys
import os
from dotenv import load_dotenv
from openai import OpenAI

# Add src to path if running from root without installing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from privalyse_mask import PrivalyseMasker

# Load environment variables
load_dotenv()

def main():
    print("🤖 Privalyse Mask - Real LLM Example")
    print("====================================")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in .env file.")
        print("Please create a .env file with your API key.")
        return

    client = OpenAI(api_key=api_key)
    masker = PrivalyseMasker(languages=["en"])

    # Sensitive input
    user_input = """
    Please write a short professional bio for John Doe, 
    born on 23.08.1990, who works as a Software Engineer. 
    Mention his email john.doe@example.com for contact.
    """

    print(f"\n[Original Input]:\n{user_input}")

    # 1. Mask
    masked_text, mapping = masker.mask(user_input)
    print(f"\n[Masked Input]:\n{masked_text}")

    # 2. Call LLM
    print("\n[Calling OpenAI]...")
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Use the provided placeholders exactly as they appear in your response."},
                {"role": "user", "content": masked_text}
            ],
            temperature=0.7
        )
        llm_response_text = response.choices[0].message.content
        print(f"\n[LLM Raw Response]:\n{llm_response_text}")

        # 3. Unmask
        final_response = masker.unmask(llm_response_text, mapping)
        print(f"\n[Final Unmasked Response]:\n{final_response}")

    except Exception as e:
        print(f"Error calling LLM: {e}")

if __name__ == "__main__":
    main()
