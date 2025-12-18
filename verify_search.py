import sys
import os
import django
from pathlib import Path

# Setup Django environment
BASE_DIR = Path("C:/projects/pharmacy_app")
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy.settings')
django.setup()

from store.models import Medicine
from chatbot_api.app.pharmacy_bot import PharmacyBot

def verify_search_logic():
    print(f"--- Verifying Medicine Search Enhancements ---")
    
    # 1. List Available Medicines
    print("\n[DB Content] Available Medicines:")
    all_meds = Medicine.objects.all()
    if not all_meds:
        print("  (Database is empty. Creating a mock Paracetamol for testing...)")
        Medicine.objects.create(name="Paracetamol 500mg", price=5.00, category="Painkiller", description="Relieves pain and fever.")
        Medicine.objects.create(name="Ibuprofen 200mg", price=8.50, category="Painkiller", description="Anti-inflammatory.")
        all_meds = Medicine.objects.all()

    for m in all_meds:
        print(f"  - {m.name}")
        
    bot = PharmacyBot()
    
    # 2. Test Cases
    test_queries = [
        "price of Panadol",      # Alias -> Paracetamol
        "do you have pandol",    # Typo of Alias -> Paracetamol
        "cost of paractamol",    # Typo of Official -> Paracetamol
        "buy advil",             # Alias -> Ibuprofen
        "get brufen",            # Alias -> Ibuprofen
        "price of xyz123"        # Unknown
    ]
    
    print("\n[Search Tests]")
    for q in test_queries:
        print(f"\nQuery: '{q}'")
        response = bot.process_instruction(q)
        # Check if response contains the expected medicine name
        # We assume "Paracetamol" or "Ibuprofen" will be in the output if found
        
        found = False
        if "Paracetamol" in response and ("Panadol" in q or "pandol" in q or "paractamol" in q):
            found = True
        elif "Ibuprofen" in response and ("advil" in q or "brufen" in q):
            found = True
        elif "No matches found" in response and "xyz123" in q:
            found = True
            
        status = "PASSED" if found else "FAILED"
        print(f"  Result: {status}")
        print(f"  Output Snippet: {response.splitlines()[0] if response else 'Empty'}")

if __name__ == "__main__":
    verify_search_logic()
