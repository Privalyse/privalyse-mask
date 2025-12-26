import sys
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

# Add src to path if running from root without installing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from privalyse_mask import PrivalyseMasker

# Load environment variables
load_dotenv()

def main():
    print("🦜🔗 Privalyse Mask - LangChain Example")
    print("======================================")

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found.")
        return

    masker = PrivalyseMasker(languages=["en"])
    model = ChatOpenAI(model="gpt-3.5-turbo")

    # Define the masking step
    def mask_step(inputs):
        text = inputs["text"]
        masked_text, mapping = masker.mask(text)
        return {"masked_text": masked_text, "mapping": mapping}

    # Define the unmasking step
    def unmask_step(inputs):
        response_text = inputs["response"]
        mapping = inputs["mapping"]
        return masker.unmask(response_text, mapping)

    # Prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Use the placeholders provided in the input."),
        ("user", "{masked_text}")
    ])

    # Build the chain
    # 1. Mask Input -> 2. Prompt -> 3. Model -> 4. Unmask
    
    # Note: In a real chain, passing 'mapping' through the model step requires 
    # using RunnablePassthrough or similar to keep it in context.
    # Here is a simplified explicit flow:
    
    chain = (
        RunnableLambda(mask_step) 
        | {
            "response": (lambda x: x["masked_text"]) | prompt | model | StrOutputParser(),
            "mapping": lambda x: x["mapping"]
        } 
        | RunnableLambda(unmask_step)
    )

    # Sensitive input
    user_input = "My name is Sarah Connor and I need to hide from the Terminator."
    
    print(f"\n[Original Input]: {user_input}")
    
    # Run Chain
    print("\n[Running Chain]...")
    result = chain.invoke({"text": user_input})
    
    print(f"\n[Final Result]: {result}")

if __name__ == "__main__":
    main()
