import os
import sys
import json
import django

# Setup Django/Paths
sys.path.append('C:/projects/pharmacy_app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy.settings')
django.setup()

from chatbot_api.app.health_bot import HealthBot

def run_verification():
    print("--- 🏥 Verifying Health RAG Retrieval 🏥 ---\n")
    
    bot = HealthBot()
    
    queries = [
        ("What are the side effects of Lisinopril?", "Lisinopril"),
        ("Can I take aspirin on an empty stomach?", "Stomach bleeding"),
        ("What is the recommended dosage for Paracetamol for a child?", "Acetaminophen"),
        ("Is it safe to mix alcohol with antibiotics?", "Alcohol") 
    ]
    
    # helper to find raw text in corpus
    def find_in_corpus(keyword):
        for doc in bot.documents:
            if keyword.lower() in doc['text'].lower():
                return True
        return False

    for query, expected_keyword in queries:
        print(f"\n❓ Query: {query}")
        response = bot.search(query)
        print(f"🤖 Bot Response Summary: {response[:150]}...") 
        
        # Validation
        in_db = find_in_corpus(expected_keyword)
        print(f"   - Keyword '{expected_keyword}' found in local Corpus? {'✅ YES' if in_db else '❌ NO'}")
        
        if expected_keyword.lower() in response.lower():
             print(f"   - Bot retrieved correct context? ✅ YES")
        else:
             print(f"   - Bot retrieved correct context? ⚠️ CHECK (Might use synonym)")

    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    run_verification()
