# Integrations

Privalyse Mask is designed to sit between your application and the AI provider.

## OpenAI

When using the OpenAI SDK, wrap your prompt construction with the masking logic.

```python
from openai import OpenAI
from privalyse_mask import PrivalyseMasker

client = OpenAI()
masker = PrivalyseMasker()

def secure_chat(user_message):
    # 1. Mask
    masked_message, mapping = masker.mask(user_message)
    
    # 2. Call API
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": masked_message}]
    )
    llm_content = response.choices[0].message.content
    
    # 3. Unmask
    return masker.unmask(llm_content, mapping)

print(secure_chat("My email is alice@example.com"))
```

## LangChain

You can integrate Privalyse Mask as a custom component or a pre/post-processing step in a LangChain chain.

```python
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from privalyse_mask import PrivalyseMasker

masker = PrivalyseMasker()
model = ChatOpenAI()

def mask_step(inputs):
    text = inputs["text"]
    masked, mapping = masker.mask(text)
    return {"masked_text": masked, "mapping": mapping}

def unmask_step(inputs):
    response_text = inputs["response"].content
    mapping = inputs["mapping"]
    return masker.unmask(response_text, mapping)

# Simple Chain
chain = (
    RunnableLambda(mask_step) 
    | {
        "response": lambda x: model.invoke(x["masked_text"]),
        "mapping": lambda x: x["mapping"]
    } 
    | RunnableLambda(unmask_step)
)

result = chain.invoke({"text": "Call John at 555-0123"})
print(result)
```

## RAG Pipelines (Retrieval-Augmented Generation)

In RAG pipelines, PII can exist in both the **Knowledge Base** (documents) and the **User Query**.

### Strategy 1: Masking at Ingestion (Recommended)

1.  **Ingestion**: Mask documents *before* embedding and indexing. Store the `mapping` alongside the vector (in metadata) or in a separate secure store.
2.  **Query**: Mask the user query using the *same seed* (if you want consistent hashing across the DB) or just mask it to protect the query itself.
    *   *Note*: If you mask documents with `{Name_x92}` and the query with `{Name_y55}`, vector search might fail to match. You must use a consistent `seed` and ensure deterministic hashing if you want to match entities.
    *   Alternatively, mask the query for privacy, but rely on the semantic context (e.g., "the manager") for retrieval if exact entity matching isn't required.

### Strategy 2: Masking at Query Time (Privacy Firewall)

1.  **Ingestion**: Store raw documents (if compliant) or use a private vector DB.
2.  **Query**:
    1.  Retrieve relevant documents (raw).
    2.  Mask the *combined* context (Query + Retrieved Docs).
    3.  Send masked context to LLM.
    4.  Unmask response.

This strategy is easier to implement if you already have a vector DB, as it treats the RAG retrieval as a trusted internal component and only protects the external LLM call.

```python
# Example of Strategy 2 (Masking Context)

retrieved_docs = ["Doc 1: Alice is the CEO.", "Doc 2: Bob is the CTO."]
query = "Who is the CEO?"

# Combine
context = "\n".join(retrieved_docs)
full_prompt = f"Context:\n{context}\n\nQuestion: {query}"

# Mask everything before sending to LLM
masked_prompt, mapping = masker.mask(full_prompt)

# ... send to LLM ...
```
