import json
import os
import sys
from typing import Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

# Add src to path for local testing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from privalyse_mask import PrivalyseMasker

# Load environment variables
load_dotenv()

def mock_database_lookup(name: str, email: str) -> str:
    """
    A mock 'real' tool that requires actual PII to work.
    """
    # In a real system, this would query a SQL DB or CRM
    db = {
        "Peter Parker": {"status": "Active", "role": "Photographer"},
        "peter.parker@dailybugle.com": {"status": "Active", "role": "Photographer"},
        "Tony Stark": {"status": "VIP", "role": "CEO"},
    }
    
    key = name if name in db else email
    if key in db:
        return json.dumps(db[key])
    return json.dumps({"error": "User not found"})

def main():
    print("🛠️  Secure Tool Calling Example")
    print("------------------------------")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  Warning: OPENAI_API_KEY not found. Using mock mode.")
        client = None
    else:
        client = OpenAI(api_key=api_key)

    masker = PrivalyseMasker()

    # 1. User Input with PII
    user_input = "Check the status of Peter Parker (peter.parker@dailybugle.com) in the database."
    print(f"\n[Original Input]: {user_input}")

    # 2. Mask Input
    masked_input, mapping = masker.mask(user_input)
    print(f"[🔒 Masked Input]: {masked_input}")

    # Define tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_user_status",
                "description": "Get user status from database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "The user's full name"},
                        "email": {"type": "string", "description": "The user's email address"},
                    },
                    "required": ["name"],
                },
            },
        }
    ]

    # 3. LLM Call (Simulated or Real)
    print("\n[🤖 LLM Thinking]...")
    
    if client:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": masked_input}],
            tools=tools,
            tool_choice="auto",
        )
        message = response.choices[0].message
        tool_calls = message.tool_calls
    else:
        # Mocking the LLM response structure for tool call
        # The LLM sees surrogates, so it will use surrogates in arguments!
        # We need to find the surrogates from the mapping to simulate this correctly
        name_surrogate = next((k for k in mapping.keys() if "Name_" in k), "{Name_Unknown}")
        email_surrogate = next((k for k in mapping.keys() if "Email_" in k), "{Email_Unknown}")
        
        class MockToolCall:
            def __init__(self, name, args):
                self.function = type('obj', (object,), {'name': name, 'arguments': args})
        
        tool_calls = [
            MockToolCall(
                "get_user_status", 
                json.dumps({"name": name_surrogate, "email": email_surrogate})
            )
        ]

    # 4. Handle Tool Call
    if tool_calls:
        for tool_call in tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)
            
            print(f"   [⚠️  LLM wants to call]: {func_name}({func_args})")
            print("   -> Arguments are masked! The DB won't find them.")

            # 5. Unmask Arguments
            # We must restore PII so the tool can execute
            real_name = masker.unmask(func_args.get("name", ""), mapping)
            real_email = masker.unmask(func_args.get("email", ""), mapping)
            
            print(f"   [🔓 Unmasking Args]: name='{real_name}', email='{real_email}'")
            
            # 6. Execute Real Tool
            tool_result = mock_database_lookup(real_name, real_email)
            print(f"   [✅ Tool Output]: {tool_result}")
            
            # 7. (Optional) Mask Tool Output
            # If the tool returns PII, we should mask it before sending back to LLM
            # In this simple case, the output is just status/role, so maybe safe.
            # But let's be safe:
            safe_tool_output, _ = masker.mask(tool_result)
            print(f"   [🔒 Safe Output to LLM]: {safe_tool_output}")

if __name__ == "__main__":
    main()
