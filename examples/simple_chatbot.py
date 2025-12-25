import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Add src to path for local testing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from privalyse_mask import PrivalyseMasker

# Load environment variables
load_dotenv()

def main():
    print("🤖 Secure Chatbot (Privalyse Mask Demo)")
    print("---------------------------------------")
    print("Type 'exit' to quit.\n")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  Warning: OPENAI_API_KEY not found. Using mock mode.")
        client = None
    else:
        client = OpenAI(api_key=api_key)

    masker = PrivalyseMasker(languages=["en", "de"])

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        # 1. Mask Input
        masked_input, mapping = masker.mask(user_input)
        
        # Show what the LLM sees (Debug)
        print(f"   [🔒 LLM sees]: {masked_input}")

        # 2. Get Response
        if client:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": masked_input}]
            )
            llm_response = response.choices[0].message.content
        else:
            # Mock response
            llm_response = f"I processed your request about {masked_input}."

        # 3. Unmask Response
        final_response = masker.unmask(llm_response, mapping)

        print(f"Bot: {final_response}\n")

if __name__ == "__main__":
    main()
