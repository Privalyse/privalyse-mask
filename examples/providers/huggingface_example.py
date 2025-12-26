import sys
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Add src to path if running from root without installing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from privalyse_mask import PrivalyseMasker

# Load environment variables
load_dotenv()

def main():
    print("🤗 Privalyse Mask - Hugging Face Inference API Example")
    print("====================================================")

    api_key = os.getenv("HF_TOKEN")
    if not api_key:
        print("❌ Error: HF_TOKEN not found in .env file.")
        return

    # Initialize Client
    client = InferenceClient(token=api_key)
    
    masker = PrivalyseMasker(languages=["en"])

    # Sensitive input
    user_input = """
    Analyze the sentiment of this customer feedback:
    "I am very angry with John Doe from Support. He was rude on 12.05.2024."
    """

    print(f"\n[Original Input]:\n{user_input}")

    # 1. Mask
    masked_text, mapping = masker.mask(user_input)
    print(f"\n[Masked Input]:\n{masked_text}")

    # 2. Call Hugging Face (Llama 3)
    print("\n[Calling Hugging Face (Llama 3)]...")
    try:
        # Using the chat completion API which is compatible with many models
        response = client.chat_completion(
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            messages=[
                {"role": "system", "content": "You are a sentiment analyzer. Keep all placeholders intact."},
                {"role": "user", "content": masked_text}
            ],
            max_tokens=500
        )
        
        llm_response = response.choices[0].message.content
        print(f"\n[LLM Response (Masked)]:\n{llm_response}")

        # 3. Unmask
        final_text = masker.unmask(llm_response, mapping)
        print(f"\n[Final Response (Unmasked)]:\n{final_text}")

    except Exception as e:
        print(f"Error calling Hugging Face: {e}")

if __name__ == "__main__":
    main()
