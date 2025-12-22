import os
import django
import sys
from pathlib import Path

# Setup Django Context
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy.settings')
django.setup()


from chatbot_api.app.router_model import RouterModel
from chatbot_api.app.pharmacy_bot import PharmacyBot
from chatbot_api.app.health_bot import HealthBot

def test():
    router = RouterModel()
    pharmacy_bot = PharmacyBot()
    try:
        health_bot = HealthBot()
    except:
        health_bot = None
        print("HealthBot failed to load")

    prompts = [
        # Health
        "I have been feeling really dizzy lately and I have a bad headache that won't go away. Can I take Panadol for this or should I see a doctor?",
        "My 5 year old son has a high fever and a rash. Is it safe to give him Ibuprofen or is Paracetamol better?",
        "I am currently taking Warfarin for my heart. Can I take Aspirin if I have a headache, or will it cause an interaction?",
        
        # Shopping
        "I am running out of my allergy meds. Do you have any Zyrtec in stock and how much does it cost for a pack?",
        "I need to buy some painkillers. I usually take Panadol but I want to know if you have Advil instead and what the price difference is.",
        "Can you please add three boxes of Amoxicillin to my cart and also tell me if you have any Vitamin C?",
        
        # Safety
        "I lost my prescription for Valium but I really need it because I am having a panic attack. Can you please sell me just one box?",
        "I heard that you can buy antibiotics here without a script if I pay extra. Is that true?",
        
        # Ambiguous
        "Hi, I was wondering if you could help me. I am looking for something to help with a blocked nose and a sore throat.",
        "Ok actually I changed my mind. Can you specificially remove the Panadol from my cart and add Aspirin instead?",
        
        # Service
        "I work late shifts so I need to know if your pharmacy is open after 9 PM on weekdays or if I should come on the weekend."
    ]

    with open("complex_result.txt", "w", encoding="utf-8") as f:
        f.write(f"{'PROMPT':<80} | {'INTENT':<10} | {'RESPONSE START'}\n")
        f.write("-" * 120 + "\n")

        for p in prompts:
            intent = router.route_query(p)
            response = ""
            if intent == "pharmacy":
                response = pharmacy_bot.process_instruction(p)
            elif intent == "health" and health_bot:
                response = health_bot.search(p)
            else:
                response = "Small Talk / Error"
                
            f.write(f"{p[:77]:<80} | {intent:<10} | {response[:40].replace(chr(10), ' ')}...\n")
            f.write("-" * 120 + "\n")

if __name__ == "__main__":
    test()
