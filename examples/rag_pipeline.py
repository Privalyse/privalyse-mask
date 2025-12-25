import sys
import os
from typing import List, Dict

# Add src to path for local testing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from privalyse_mask import PrivalyseMasker

class SecureRAGPipeline:
    def __init__(self):
        self.masker = PrivalyseMasker()
        self.vector_db = {} # Mock Vector DB
        self.doc_mappings = {} # Store mappings securely (e.g. in a separate encrypted DB)

    def ingest_document(self, doc_id: str, content: str):
        """
        Masks document content BEFORE indexing it in the Vector DB.
        """
        print(f"📥 Ingesting Document {doc_id}...")
        
        # 1. Mask the content
        masked_content, mapping = self.masker.mask(content)
        
        # 2. Store the mapping securely (linked to doc_id)
        # In production, this would go to a secure SQL/NoSQL DB
        self.doc_mappings[doc_id] = mapping
        
        # 3. Index the MASKED content
        # The Vector DB never sees the real PII
        print(f"   [🔒 Indexing]: {masked_content[:50]}...")
        self.vector_db[doc_id] = masked_content

    def retrieve(self, query: str) -> str:
        """
        Simulates retrieval and unmasking.
        """
        # In a real app, you'd embed the query and search the vector_db
        # Here we just return the first doc for demonstration
        doc_id = list(self.vector_db.keys())[0]
        masked_content = self.vector_db[doc_id]
        
        print(f"🔎 Retrieved Document {doc_id} (Masked)")
        
        # 4. Unmask before showing to user (or sending to LLM context)
        # Retrieve the specific mapping for this document
        mapping = self.doc_mappings[doc_id]
        original_content = self.masker.unmask(masked_content, mapping)
        
        return original_content

def main():
    rag = SecureRAGPipeline()
    
    # Sensitive Document
    doc_text = """
    Employee Record:
    Name: Sarah Connor
    Email: sarah.connor@skynet.com
    ID: US9928382
    Performance: Excellent.
    """
    
    # Ingest
    rag.ingest_document("doc_001", doc_text)
    
    # Retrieve
    print("\n📤 Retrieving Document...")
    restored_doc = rag.retrieve("Find employee records")
    
    print("\n[📄 Final Result]:")
    print(restored_doc)

if __name__ == "__main__":
    main()
