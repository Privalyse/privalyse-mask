import sys
import os
from openai import OpenAI

# Add src to path if running from root without installing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from privalyse_mask import PrivalyseMasker

def main():
    print("🦙 Privalyse Mask - Ollama (Local) Example")
    print("==========================================")
    print("Note: Ensure Ollama is running (`ollama serve`) and you have pulled a model (e.g. `ollama pull llama3`).")

    # Initialize OpenAI client pointing to local Ollama instance
    client = OpenAI(
        base_url='http://localhost:11434/v1',
        api_key='ollama', # required, but unused
    )
    
    masker = PrivalyseMasker(languages=["en"])

    # Sensitive input
    user_input = """
    Summarize the medical report for patient John Smith (DOB: 1985-10-20).
    Diagnosis: Hypertension. Prescribed Lisinopril.
    Contact: 555-0199.
    """

    print(f"\n[Original Input]:\n{user_input}")

    # 1. Mask
    masked_text, mapping = masker.mask(user_input)
    print(f"\n[Masked Input]:\n{masked_text}")

    # 2. Call Ollama
    print("\n[Calling Ollama (llama3)]...")
    try:
        response = client.chat.completions.create(
            model="llama3", # Change to your local model
            messages=[
                {"role": "system", "content": "You are a medical assistant. Maintain all placeholders (e.g. {Name_...}) in your summary."},
                {"role": "user", "content": masked_text}
            ],
        )
        
        llm_response = response.choices[0].message.content
        print(f"\n[LLM Response (Masked)]:\n{llm_response}")

        # 3. Unmask
        final_text = masker.unmask(llm_response, mapping)
        print(f"\n[Final Response (Unmasked)]:\n{final_text}")

    except Exception as e:
        print(f"Error calling Ollama: {e}")
        print("Hint: Is Ollama running? Try 'ollama serve' in a separate terminal.")

if __name__ == "__main__":
    main()
