import sys
import os
import django
from pathlib import Path

# Setup Django environment
BASE_DIR = Path("C:/projects/pharmacy_app")
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy.settings')
django.setup()

from chatbot_api.app.pharmacy_bot import PharmacyBot
from chatbot_api.app.router_model import RouterModel

def verify_chat_logic():
    print(f"--- Verifying Chatbot Improvements 'ho' & Fallback ---")
    
    bot = PharmacyBot()
    router = RouterModel()
    
    # 1. Test "ho"
    typo = "ho"
    intent = router.route_query(typo)
    response = bot.process_instruction(typo)
    is_greeting = "Hello! I am your Pharmacy Assistant" in response
    print(f"[Test 1] Input: '{typo}' -> Intent: {intent} | Bot Greeted? {is_greeting}")

    # 2. Test Fallback
    unknown_input = "zxczxczxc"
    response = bot.process_instruction(unknown_input)
    print(f"[Test 2] Input: '{unknown_input}'")
    print(f"  Response start: '{response[:20]}...'")
    if "I am not sure" in response:
        print("  -> PASSED: Got 'I am not sure'")
    else:
        print("  -> FAILED: Got unexpected response")

if __name__ == "__main__":
    verify_chat_logic()
