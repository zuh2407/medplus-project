import os
import django
import sys

sys.path.append('c:\\projects\\pharmacy_app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy.settings')
django.setup()

from chatbot_api.app.pharmacy_bot import PharmacyBot

bot = PharmacyBot()
queries = [
    "is ur store ope n after 9pm",
    "when do u close",
    "what are ur hours"
]

print("Running Typo Correction Verification...")
for q in queries:
    corrected = bot.correct_typos(q)
    print(f"Original: '{q}' -> Corrected: '{corrected}'")
    
    response = bot.process_instruction(q)
    if "Store Hours" in response:
        print("[PASS] Response contains Store Hours.")
    else:
        print("[FAIL] Response does NOT contain Store Hours.")
        print(f"Response: {response[:50]}...")
    print("-" * 20)
