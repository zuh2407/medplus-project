from store.models import Medicine
from django.db.models import Q
import random
import difflib
import re

# Common Drug Aliases (Synonyms/Slang -> Official Name)
MEDICINE_ALIASES = {
    # Painkillers
    "panadol": "paracetamol",
    "tylenol": "paracetamol",
    "acetaminophen": "paracetamol",
    "advil": "ibuprofen",
    "brufen": "ibuprofen",
    "motrin": "ibuprofen",
    "aspirin": "acetylsalicylic acid",
    "disprin": "acetylsalicylic acid",
    "voltarol": "diclofenac",
    "voltaren": "diclofenac",
    
    # Antibiotics
    "augmentin": "amoxicillin",
    "amoxil": "amoxicillin",
    "z-pak": "azithromycin",
    "zithromax": "azithromycin",
    "cipro": "ciprofloxacin",
    
    # Stomach
    "pepto": "bismuth subsalicylate",
    "tums": "calcium carbonate",
    "nexium": "esomeprazole",
    "prilosec": "omeprazole",
    
    # Allergies
    "benadryl": "diphenhydramine",
    "zyrtec": "cetirizine",
    "claritin": "loratadine",
    
    # General terms (mapping to a likely candidate if safe, or ignored)
    "painkiller": "paracetamol", # Default easy painkiller
    "headache": "paracetamol",
    "fever": "paracetamol",
    "flu": "ibuprofen",
}

# Synonyms for determining if user wants to search/buy something
SEARCH_INTENT_KEYWORDS = [
    "price", "cost", "how much", "rate",
    "have", "stock", "available", "do you have",
    "buy", "purchase", "order", "get", "need", "want", "looking for", "find", "search", "take",
    "medicine", "drug", "tablet", "capsule", "syrup", "pill"
]

class PharmacyBot:
    def __init__(self):
        self.sessions = {} # {session_id: {"last_search": [Medicine], "last_added": Medicine}}

    def find_medicines(self, text: str) -> list:
        """Helper to find medicines based on text."""
        medicines = Medicine.objects.all()
        found_medicines = []
        
        query_words = text.split()
        all_medicines = list(medicines) 
        all_med_names = [m.name.lower() for m in all_medicines if m.name]
        
        for word in query_words:
            if len(word) <= 3: continue 
            if word in SEARCH_INTENT_KEYWORDS: continue 
            if word in ["does", "the", "for", "with", "and", "from", "all"]: continue 
            
            candidates = {word}
            if word in MEDICINE_ALIASES:
                candidates.add(MEDICINE_ALIASES[word])
                
            alias_matches = difflib.get_close_matches(word, MEDICINE_ALIASES.keys(), n=1, cutoff=0.8)
            if alias_matches:
                candidates.add(MEDICINE_ALIASES[alias_matches[0]])
            
            db_matches = difflib.get_close_matches(word, all_med_names, n=1, cutoff=0.7)
            if db_matches:
                candidates.add(db_matches[0])

            # Priority Search: Name Matches First
            query_name = Q()
            query_desc = Q()
            for term in candidates:
                query_name |= Q(name__icontains=term)
                query_desc |= Q(description__icontains=term)
            
            # 1. Try finding by Name (Precision)
            matches = medicines.filter(query_name)
            
            # 2. If no name matches, fallback to Description (Recall for symptoms like "Headache")
            if not matches.exists():
                matches = medicines.filter(query_desc)
                
            for p in matches:
                 if p.name not in [fp.name for fp in found_medicines]:
                    found_medicines.append(p)
        
        if found_medicines:
             # Robust Sort
             found_medicines.sort(key=lambda m: difflib.SequenceMatcher(None, (m.name or "").lower(), text).ratio(), reverse=True)
             
        return found_medicines

    def process_instruction(self, text: str, session_id: str = None) -> str:
        text = text.lower()
        
        # 0. Safety/Exit Check
        if any(x in text for x in ["bye", "see you", "c u", "later", "goodbye"]):
            return "Goodbye! Have a healthy day! 👋"
            
        # 0.1 Safety Guardrail (Illegal/Unethical Requests)
        # Prevents "buy without script" type queries
        illegal_patterns = [
            r"without\s+(a\s+)?(script|prescription|rx)",
            r"no\s+(script|prescription|rx)",
            r"illegal",
            r"under\s+(the\s+)?table"
        ]
        for pattern in illegal_patterns:
            if re.search(pattern, text):
                return "I cannot fulfill requests for prescription medication without a valid prescription. Please consult your doctor or pharmacist. 🛑"

        # 1. Session Context Handling (Yes/Add it)
        confirmation_keywords = ["yes", "sure", "add it", "add to cart", "okay", "ok", "please", "take", "want", "buying", "correct", "right"]
        if session_id and session_id in self.sessions:
            context = self.sessions[session_id]
            last_search = context.get("last_search", [])
            
            # Contextual Add (User confirms previous search)
            # E.g. "Okay, I'll take two of those"
            if any(k in text for k in confirmation_keywords) and last_search:
                # Relaxed length check (was < 5, now < 15 to allow conversational confirmation)
                if len(text.split()) < 15: 
                    target_med = last_search[0]
                    
                    # Quantity Parsing
                    qty = 1
                    words = text.split()
                    qty_map = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
                    
                    for w in words:
                        if w.isdigit():
                            qty = int(w)
                            break
                        if w in qty_map:
                            qty = qty_map[w]
                            break
                    
                    return self.add_to_cart_direct(target_med, quantity=qty, session_id=session_id)

        # 2. Cart Management Logic
        if "add" in text and ("cart" in text or text.strip().startswith("add") or " buy " in text):
             # Check for "Add All"
             if " all " in f" {text} " or text.endswith(" all"):
                 # Bulk Add Logic
                 # 1. Try to find medicines in the text (e.g. "add all panadol")
                 found = self.find_medicines(text)
                 
                 # 2. If no medicines found in text, use Context (e.g. "add all")
                 if not found and session_id and session_id in self.sessions:
                     found = self.sessions[session_id].get("last_search", [])
                 
                 if found:
                     msg = "Added the following to your cart:\n"
                     total_added = 0
                     from store.models import CartItem
                     
                     for med in found:
                         self.add_to_cart_direct(med, session_id=session_id) # Reuse method (it updates context, which is fine)
                         msg += f"- {med.name}\n"
                         total_added += 1
                     
                     msg += f"\nTotal Items: {total_added}"
                     return msg
                 else:
                     return "I couldn't find any medicines to add. Please specify, e.g., 'Add all Panadol'."

             result = self.manage_cart(text, action="add", session_id=session_id)
             
             if result.startswith("I couldn't identify") and session_id and session_id in self.sessions:
                 context = self.sessions[session_id]
                 last_search = context.get("last_search", [])
                 if last_search:
                      return self.add_to_cart_direct(last_search[0], session_id=session_id)
             
             if result: return result
             
        if ("remove" in text or "delete" in text or "delte" in text or "cancel" in text):
            return self.manage_cart(text, action="remove", session_id=session_id)
            
        greetings = ["hello", "hi", "hey", "hu", "hy", "helo", "hlo", "hii", "heyy", "ho"]
        if any(g in text.split() for g in greetings) or any(g in text for g in ["hello", "good morning"]):
            return "Hello! I am your Pharmacy Assistant.\n\nI can help you Check Prices, Check Stock, Process Prescriptions, or Manage your Cart (e.g. search for a medicine and just say 'Yes' to add it).\n\nHow can I help you today?"
        
        if any(k in text for k in SEARCH_INTENT_KEYWORDS):
            # Check for Vague/Incomplete queries (e.g. "I need medicine for")
            # If the user stops at "for" or just says "I need medicine", we should ask for specifics
            # rather than searching for "medicine" or typos of it.
            vague_pattern = r"(need|want|get|buy)\s+(some\s+)?(medicine|medication|drug|pill|tablets?)s?\s*(for)?\s*$"
            if re.search(vague_pattern, text):
                return "Please specify what you need the medicine for (e.g. for headache, fever, or pain). 💊"

            if session_id:
                if session_id not in self.sessions:
                    self.sessions[session_id] = {}
                self.sessions[session_id]["last_search"] = []

            found_medicines = self.find_medicines(text)
            
            if found_medicines:
                if session_id:
                    self.sessions[session_id]["last_search"] = found_medicines
                
                response = "We have this in store:\n\n"
                for p in found_medicines[:5]: 
                    response += f"{p.name}\n"
                    response += f"Price: ${p.price}\n\n"
                
                response += "Would you like to add this to your cart?"
                return response
            else:
                return "Sorry, we don't have that medicine in our store at the moment."

        if "time" in text or "hour" in text or "open" in text or "close" in text or "when" in text or "available" in text:
            return (
                "Here are our Service Hours:\n\n"
                "Store Hours:\n"
                "- Mon-Fri: 8:00 AM - 10:00 PM\n"
                "- Sat-Sun: 9:00 AM - 9:00 PM\n\n"
                "Pharmacist Availability:\n"
                "- Mon-Fri: 9:00 AM - 6:00 PM\n"
                "- Sat: 10:00 AM - 4:00 PM"
            )

        return "I am not sure I understood that. You can ask me to check prices, find medicines, or add items to your cart. How can I help?"

    def add_to_cart_direct(self, medicine, quantity=1, session_id=None) -> str:
        from store.models import CartItem
        item, created = CartItem.objects.get_or_create(medicine=medicine)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()
        
        if session_id and session_id in self.sessions:
             self.sessions[session_id]["last_search"] = [] 
             self.sessions[session_id]["last_added"] = medicine
             
        return f"{quantity} x {medicine.name} added to your cart.\n\nCurrent Cart Total: ${sum(i.get_total_price() for i in CartItem.objects.all())}"

    def manage_cart(self, text: str, action: str, session_id: str = None) -> str:
        from store.models import CartItem, Medicine 
        
        words = text.split()
        quantity = 1
        qty_map = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
        
        for w in words:
            if w.isdigit():
                quantity = int(w)
                break
            if w in qty_map:
                quantity = qty_map[w]
                break
                
        medicines = Medicine.objects.all()
        target_med = None
        all_medicines = sorted(list(medicines), key=lambda x: len(x.name), reverse=True)
        
        for med in all_medicines:
            if med.name.lower() in text:
                target_med = med
                break
        
        if not target_med and action == "remove" and session_id and session_id in self.sessions:
             last_added = self.sessions[session_id].get("last_added")
             if last_added:
                 target_med = last_added

        if not target_med:
             return "I couldn't identify the medicine name to add/remove. Please say the exact product name, e.g., 'Add Panadol to cart'."

        if action == "add":
            item, created = CartItem.objects.get_or_create(medicine=target_med)
            if not created:
                item.quantity += quantity
            else:
                item.quantity = quantity
            item.save()
            
            if session_id and session_id in self.sessions:
                self.sessions[session_id]["last_search"] = []
                self.sessions[session_id]["last_added"] = target_med
                
            return f"{quantity} x {target_med.name} added to your cart.\n\nCurrent Cart Total: ${sum(i.get_total_price() for i in CartItem.objects.all())}"
            
        elif action == "remove":
            try:
                item = CartItem.objects.get(medicine=target_med)
                item.delete()
                
                if session_id and session_id in self.sessions:
                    if self.sessions[session_id].get("last_added") == target_med:
                         self.sessions[session_id]["last_added"] = None

                return f"{target_med.name} removed from your cart."
            except CartItem.DoesNotExist:
                return f"{target_med.name} is not in your cart."
                
        return "I didn't understand that cart command."

    def process_prescription(self, filename: str, content: bytes) -> dict:
        all_medicines = list(Medicine.objects.all())
        if not all_medicines:
             return {"message": "Database Empty\n\nNo medicines found in the system.", "products": []}
             
        suggestions = random.sample(all_medicines, min(len(all_medicines), 2))
        
        results = []
        for p in suggestions:
            results.append({
                "id": p.id,
                "name": p.name,
                "price": str(p.price),
                "image_url": p.image.url if p.image else "",
                "description": p.description[:100] + "..."
            })
            
        msg = "Prescription Analyzed\n\n"
        msg += "We analyzed your file and identified the following potential matches from our inventory:\n\n"
        for p in suggestions:
             msg += f"{p.name}\n"
             msg += f"Price: ${p.price}\n"
        
        msg += "\nPlease confirm these are the correct items before ordering."

        return {
            "message": msg,
            "products": results
        }
