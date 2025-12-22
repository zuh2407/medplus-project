import os
import django
import sys

sys.path.append('c:\\projects\\pharmacy_app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy.settings')
django.setup()

from chatbot_api.app.pharmacy_bot import PharmacyBot, SEARCH_INTENT_KEYWORDS

bot = PharmacyBot()
query = "can u tell me if u have panadol"

# 1. Check Typos
corrected = bot.correct_typos(query)
print(f"Original: '{query}'")
print(f"Corrected: '{corrected}'")

# 2. Check Keyword Match
text = corrected.lower()
matches = [k for k in SEARCH_INTENT_KEYWORDS if k in text]
print(f"Keywords found: {matches}")

# 3. Check Find Medicines
meds = bot.find_medicines(text)
print(f"Found Meds: {[m.name for m in meds]}")

# 4. Run Process
response = bot.process_instruction(query, session_id="debug_sess_3")
print(f"Response Preview: {response[:50]}...")
