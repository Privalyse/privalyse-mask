import time
import sys
from privalyse_mask import PrivalyseMasker

# ANSI Colors
BOLD = "\033[1m"
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def type_writer(text, speed=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()

def main():
    # Clear screen
    print("\033[H\033[J", end="")
    
    print(f"{BOLD}🛡️  Privalyse Mask Demo{RESET}\n")
    time.sleep(0.5)

    masker = PrivalyseMasker()
    
    # Scenario
    input_text = "Contact Peter Parker at peter.parker@dailybugle.com regarding the incident in New York."
    
    print(f"{BOLD}1. Sensitive Input (PII):{RESET}")
    print(f"   \"{input_text}\"\n")
    time.sleep(1.5)

    # Masking
    print(f"{BOLD}2. Applying Privalyse Mask...{RESET}")
    masked_text, mapping = masker.mask(input_text)
    time.sleep(0.8)
    
    # Show Masked
    print(f"{GREEN}   ✔ Masked Output (Safe for LLM):{RESET}")
    print(f"   \"{masked_text}\"\n")
    time.sleep(2)

    # Simulating LLM
    print(f"{BOLD}3. Sending to LLM...{RESET}")
    time.sleep(1.0)
    
    # Find the name surrogate dynamically
    name_surrogate = next((k for k in mapping.keys() if "Name_" in k), "{Name_Unknown}")
    
    llm_response_masked = f"I have sent an email to {name_surrogate} regarding the New York situation."
    print(f"{BLUE}   🤖 LLM Response (Context-Aware):{RESET}")
    print(f"   \"{llm_response_masked}\"\n")
    time.sleep(2)

    # Unmasking
    print(f"{BOLD}4. Unmasking Response...{RESET}")
    final_response = masker.unmask(llm_response_masked, mapping)
    time.sleep(0.5)
    print(f"{YELLOW}   ✨ Final Result (Restored):{RESET}")
    type_writer(f"   \"{final_response}\"")
    print("\n")

if __name__ == "__main__":
    main()
