import os
import django
import sys

sys.path.append('c:\\projects\\pharmacy_app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy.settings')
django.setup()

from store.models import Medicine
from chatbot_api.app.pharmacy_bot import PharmacyBot

bot = PharmacyBot()
session_id = "debug_sess_2"

# Context: Last search was Ibuprofen
ibuprofen = Medicine.objects.filter(name__icontains="ibuprofen").first()
bot.sessions[session_id] = {
    "last_search": [ibuprofen],
    "last_added": None
}

print("Running Verification...")

# TEST 1: New Search Overrides Confirmation
query = "can u tell me if u have panadol"
response = bot.process_instruction(query, session_id=session_id)
# Expectation: Should NOT add to cart. Should return search results for Paracetamol/Panadol.
if "added to your cart" in response.lower():
    print("[FAIL] Test 1: Incorrectly added to cart.")
    print(f"Response: {response[:100]}...")
elif "paracetamol" in response.lower() or "panadol" in response.lower():
    print("[PASS] Test 1: Correctly searched for Panadol.")
else:
    print("[FAIL] Test 1: Unexpected response.")
    print(f"Response: {response}")

# TEST 2: Confirmation Works
# Reset context
bot.sessions[session_id]["last_search"] = [ibuprofen]
query_confirm = "yes please"
response_confirm = bot.process_instruction(query_confirm, session_id=session_id)

if "added to your cart" in response_confirm.lower() and "ibuprofen" in response_confirm.lower():
    print("[PASS] Test 2: Confirmation worked.")
    # Check Price Format
    if "Item Price:" in response_confirm and "Current Cart Total:" in response_confirm:
         print("[PASS] Test 2: Price format is correct.")
    else:
         print("[FAIL] Test 2: Price format incorrect.")
         print(f"Response: {response_confirm}")
else:
    print("[FAIL] Test 2: Confirmation failed.")
    print(f"Response: {response_confirm[:100]}...")
