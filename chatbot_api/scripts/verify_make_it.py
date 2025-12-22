import os
import django
import sys

sys.path.append('c:\\projects\\pharmacy_app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy.settings')
django.setup()

from store.models import Medicine
from chatbot_api.app.pharmacy_bot import PharmacyBot

bot = PharmacyBot()
session_id = "debug_sess_make"

# Setup Context: User added "Panadol" to cart (so last_added is Panadol, last_search is empty)
panadol = Medicine.objects.filter(name__icontains="panadol").first()
if not panadol:
    # Create dummy if not exists for test
    panadol = Medicine.objects.create(name="Panadol Extra", price=6.50, category="Painkiller")

bot.sessions[session_id] = {
    "last_search": [],
    "last_added": panadol
}

query = "make it 5"
print(f"Query: '{query}'")

# Check Typo Correction
corrected = bot.correct_typos(query)
print(f"Corrected: '{corrected}'")
if "take" in corrected:
    print("[FAIL] 'make' corrected to 'take'!")
else:
    print("[PASS] 'make' preserved.")

# Check Logic
response = bot.process_instruction(query, session_id=session_id)
print(f"Response: {response}")

if "Updated Panadol" in response or "Updated" in response:
    print("[PASS] Quantity updated.")
else:
    print("[FAIL] Quantity NOT updated.")
