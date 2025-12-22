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
    "valium": "diazepam",
    "xanax": "alprazolam",
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

    def correct_typos(self, text: str) -> str:
        """Corrects typos in common keywords using fuzzy matching."""
        words = text.split()
        corrected_words = []
        
        # Combine intent keywords with common stop words to avoid false positives on short words if needed
        # But here we focus on intent keywords
        target_words = SEARCH_INTENT_KEYWORDS + ["hello", "hi", "help", "cart", "remove", "add", "checkout", "open", "close", "hours", "time", "make", "dont", "prescription", "lost"]
        
        for word in words:
            # Skip numbers or very short words unless specific known ones
            if len(word) < 3 and word not in ["hi", "no", "ok"]: 
                corrected_words.append(word)
                continue
                
            # If word is already correct, keep it
            if word.lower() in target_words:
                corrected_words.append(word)
                continue
                
            # Check for close matches
            matches = difflib.get_close_matches(word.lower(), target_words, n=1, cutoff=0.7)
            if matches:
                 # Verify it's not a medicine name before replacing? 
                 # Risky if medicine names look like keywords, but unlikely for "havr" -> "have"
                 corrected_words.append(matches[0])
            else:
                 corrected_words.append(word)
                 
        return " ".join(corrected_words)

    def process_instruction(self, text: str, session_id: str = None, user_id: int = None) -> str:
        # 1. Preprocess: Typos
        text = self.correct_typos(text)
        text = text.lower()
        
        # 0. Safety/Exit Check
        if any(x in text for x in ["bye", "see you", "c u", "later", "goodbye"]):
            return "Goodbye! Have a healthy day! 👋"
            
        # 0.1 Safety Guardrail (Illegal/Unethical Requests)
        # Prevents "buy without script" type queries
        illegal_patterns = [
            r"without\s+(?:[\w]+\s+){0,3}(script|prescript|rx)",
            r"(no|dont|don't|do\s+not)\s+(have\s+)?(a\s+)?(script|prescript|rx)",
            r"illegal",
            r"under\s+(the\s+)?table",
            r"lost\s+(my\s+)?(script|prescript|rx)",
            r"lost\s+it", # Contextually risky if combined with controlled substances
            r"without\s+seeing\s+a\s+doctor"
        ]
        for pattern in illegal_patterns:
            if re.search(pattern, text):
                return "I cannot fulfill requests for prescription medication without a valid prescription. Please consult your doctor or pharmacist. 🛑"

        # 0.5 Checkout Intent (High Priority)
        if "checkout" in text or "pay" in text or "place order" in text:
            from store.models import CartItem
            cart_total = 0
            # Ensure we look at the SESSION specific cart
            if user_id:
                 cart_total = sum(i.get_total_price() for i in CartItem.objects.filter(user_id=user_id))
            elif session_id:
                cart_total = sum(i.get_total_price() for i in CartItem.objects.filter(session_id=session_id))
            else:
                # Fallback (should be avoided in multi-user)
                 cart_total = sum(i.get_total_price() for i in CartItem.objects.filter(session_id__isnull=True))
            
            if cart_total > 0:
                return f"Your total is ${cart_total:.2f}.\n\nPlease complete your payment securely here:\n\n[ Pay Now ](/checkout/)\n\nOnce paid, your order will be processed! 💳"
            else:
                return "Your cart is empty. Please add some medicines first! 💊"

        # 1.5 Cart Management Logic (Moved UP for Priority)
        # We check this BEFORE Confirmation to catch "add panadol" or "remove X" explicitly
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
                         self.add_to_cart_direct(med, session_id=session_id, user_id=user_id) # Reuse method (it updates context, which is fine)
                         msg += f"- {med.name}\n"
                         total_added += 1
                     
                     # Get updated total
                     if session_id:
                         cart_total = sum(i.get_total_price() for i in CartItem.objects.filter(session_id=session_id))
                     else:
                         cart_total = sum(i.get_total_price() for i in CartItem.objects.filter(session_id__isnull=True))

                     msg += f"\nTotal Items: {total_added}\nCurrent Cart Total: ${cart_total:.2f}"
                     return msg
                 else:
                     return "I couldn't find any medicines to add. Please specify, e.g., 'Add all Panadol'."

             result = self.manage_cart(text, action="add", session_id=session_id, user_id=user_id)
             
             if result.startswith("I couldn't identify") and session_id and session_id in self.sessions:
                 context = self.sessions[session_id]
                 last_search = context.get("last_search", [])
                 if last_search:
                      return self.add_to_cart_direct(last_search[0], session_id=session_id, user_id=user_id)
             
             if result: return result
             
        if ("remove" in text or "delete" in text or "dlete" in text or "cancel" in text or "clear" in text or "empty" in text):
            # Check for "Remove All" / "Clear Cart"
            if "all" in text or "clear" in text or "empty" in text:
                 from store.models import CartItem
                 if user_id:
                     CartItem.objects.filter(user_id=user_id).delete()
                 elif session_id:
                     CartItem.objects.filter(session_id=session_id).delete()
                     if session_id in self.sessions:
                         self.sessions[session_id]["last_added"] = None
                         self.sessions[session_id]["last_search"] = []
                 else:
                     CartItem.objects.filter(session_id__isnull=True).delete()
                 
                 return "Your cart has been cleared. 🗑️"

            return self.manage_cart(text, action="remove", session_id=session_id, user_id=user_id)

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
                    # CRITICAL: Guardrail for New Search Intent masquerading as Confirmation
                    # e.g. "I want Panadol" contains "want" -> confirmation? NO.
                    # Check if the user is naming a DIFFERENT medicine than the last search.
                    
                    found_new_meds = self.find_medicines(text)
                    # Filter out if the found med is actually the SAME as last_search (then it IS a confirmation)
                    true_new_meds = []
                    last_search_names = [m.name.lower() for m in last_search]
                    
                    for m in found_new_meds:
                        # Simple check: if name is significantly different
                        is_same = False
                        for lsn in last_search_names:
                             if m.name.lower() in lsn or lsn in m.name.lower():
                                 is_same = True
                                 break
                        if not is_same:
                             true_new_meds.append(m)
                    
                    if true_new_meds:
                        # If we found NEW medicines that are NOT the old one, pass through to Search Logic at the end
                        pass 
                    else:
                        # Ambiguity Check: If multiple items were found, don't just add the first one.
                        if len(last_search) > 1:
                             options = "\n".join([f"- {m.name} (${m.price})" for m in last_search[:5]])
                             return f"I found multiple items. Which one would you like to add?\n\n{options}\n\nPlease type the name of the item."

                        target_med = last_search[0]
                        
                        # Quantity Parsing
                        qty = 1
                        # Use pending quantity from search if available
                        if session_id and session_id in self.sessions:
                             qty = self.sessions[session_id].get("pending_quantity", 1)

                        # Allow override if user explicitly specified a NEW quantity in the confirmation
                        # e.g. "Actually make it 2"
                        # But be careful with "1st one" -> "one" maps to 1. 
                        # If "one" is present but we have a pending quantity > 1, we might prefer pending.
                        
                        qty_map = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
                        words = text.split()
                        
                        found_new_qty = False
                        temp_qty = 1
                        
                        for w in words:
                            if w.isdigit():
                                temp_qty = int(w)
                                found_new_qty = True
                                break
                            if w in qty_map:
                                 # Exclude "one" if it's likely part of "the one" or "first one" AND we have a pending quantity
                                 if w == "one" and qty > 1:
                                     continue
                                 temp_qty = qty_map[w]
                                 found_new_qty = True
                                 break
                        
                        if found_new_qty:
                            qty = temp_qty
                        
                        return self.add_to_cart_direct(target_med, quantity=qty, session_id=session_id, user_id=user_id)

            # 1.1 Handle Selection from Ambiguity (e.g. "1st one" or "Panadol Extra")
            if last_search and len(last_search) > 1:
                # Check for Ordinals (1st, 2nd, first, second)
                normalized_text = text.lower().replace("one", "").strip() # Remove "one" to handle "first one" -> "first"
                
                ordinal_map = {
                    "first": 0, "1st": 0, "1": 0,
                    "second": 1, "2nd": 1, "2": 1,
                    "third": 2, "3rd": 2, "3": 2,
                    "fourth": 3, "4th": 3, "4": 3,
                    "fifth": 4, "5th": 4, "5": 4
                }
                
                selected_index = -1
                
                # Check for explicit number/ordinal in text
                for word in text.split():
                    if word in ordinal_map:
                        selected_index = ordinal_map[word]
                        break
                
                # Check for "option X"
                if "option" in text:
                     for word in text.split():
                         if word.isdigit():
                             idx = int(word) - 1
                             if 0 <= idx < 5:
                                 selected_index = idx
                                 break

                target_med = None
                if selected_index != -1 and selected_index < len(last_search):
                    target_med = last_search[selected_index]
                
                # If no ordinal found, try Fuzzy Name Matching against the options
                if not target_med:
                    # 1. Standard DiffLib
                    possible_matches = difflib.get_close_matches(text, [m.name.lower() for m in last_search], n=1, cutoff=0.6)
                    if possible_matches:
                        for m in last_search:
                            if m.name.lower() == possible_matches[0]:
                                target_med = m
                                break
                    
                    # 2. Token-Based Matching (for "the extra one" -> "TestAmbiguity Extra")
                    if not target_med:
                        user_words = [w for w in text.split() if w not in ["the", "one", "please", "add", "option"]]
                        best_match = None
                        max_score = 0
                        
                        for m in last_search:
                            score = 0
                            lname = m.name.lower()
                            for w in user_words:
                                if w in lname:
                                    score += 1
                            
                            if score > max_score:
                                max_score = score
                                best_match = m
                            elif score == max_score:
                                best_match = None # Ambiguous if tie
                        
                        if best_match and max_score > 0:
                            target_med = best_match

                if target_med:
                    # Retrieve pending quantity (default 1)
                    qty = 1
                    if session_id and session_id in self.sessions:
                        qty = self.sessions[session_id].get("pending_quantity", 1)
                        
                    return self.add_to_cart_direct(target_med, quantity=qty, session_id=session_id, user_id=user_id)



        if ("make it" in text or "change to" in text or "update to" in text or "actually" in text or "sorry" in text):
            # 0. Ambiguity Check: If "sorry remove 1", we should let "remove" logic handle it.
            if "remove" in text or "delete" in text or "add" in text:
                 pass # Fall through to explicit Add/Remove logic
            else:
                 # Extract Number
                 new_qty = -1
                 words = text.split()
                 qty_map = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
                 
                 for w in words:
                     if w.isdigit():
                         new_qty = int(w)
                         break
                     if w in qty_map:
                         new_qty = qty_map[w]
                         break
                 
                 if new_qty > 0 and session_id and session_id in self.sessions:
                     context = self.sessions[session_id]
                     
                     # 1. Check for Pending Search Context (Prioritize this!)
                     last_search = context.get("last_search", [])
                     if last_search:
                         if len(last_search) > 1:
                             # Ambiguous: User searched "Panadol", got 3 results, then said "Make it 5".
                             # We need to know WHICH one.
                             context["pending_quantity"] = new_qty # Save the intended quantity!
                             options = "\n".join([f"- {m.name} (${m.price})" for m in last_search[:5]])
                             return f"I found multiple items. Which one would you like to make {new_qty}?\n\n{options}\n\nPlease type the name of the item."
                         else:
                             # Explicit: Only 1 item found (e.g. "Amoxicillin"), so "Make it 5" means "Add 5 Amoxicillin".
                             target_med = last_search[0]
                             return self.add_to_cart_direct(target_med, quantity=new_qty, session_id=session_id, user_id=user_id)
    
                     # 2. Fallback: Update Last Added Item (Legacy behavior) OR DB Fallback
                     from store.models import CartItem
                     last_added_med = context.get("last_added")
                     
                     # If memory is empty (server restart), try to find the latest item from DB
                     if not last_added_med:
                         item_query = CartItem.objects.all()
                         if user_id:
                             item_query = item_query.filter(user_id=user_id)
                         elif session_id:
                             item_query = item_query.filter(session_id=session_id)
                         else:
                             item_query = item_query.filter(session_id__isnull=True)
                             
                         # Get most recently created item
                         latest_item = item_query.order_by('-id').first()
                         if latest_item:
                             last_added_med = latest_item.medicine

                     if last_added_med:
                         # Find item in cart
                         item_query = CartItem.objects.filter(medicine=last_added_med)
                         if user_id:
                             item_query = item_query.filter(user_id=user_id)
                         elif session_id:
                             item_query = item_query.filter(session_id=session_id)
                         else:
                             item_query = item_query.filter(session_id__isnull=True)
                         
                         if item_query.exists():
                             item = item_query.first()
                             item.quantity = new_qty # SET the quantity (don't add)
                             item.save()
                             
                             # Recalculate Total
                             if user_id:
                                 cart_total = sum(i.get_total_price() for i in CartItem.objects.filter(user_id=user_id))
                             elif session_id:
                                 cart_total = sum(i.get_total_price() for i in CartItem.objects.filter(session_id=session_id))
                             else:
                                 cart_total = sum(i.get_total_price() for i in CartItem.objects.filter(session_id__isnull=True))
                                 
                             return f"Updated {item.medicine.name} to {new_qty} in your cart.\n\nCurrent Cart Total: ${cart_total}"
        

            
        greetings = ["hello", "hi", "hey", "hu", "hy", "helo", "hlo", "hii", "heyy", "ho"]
        if any(g in text.split() for g in greetings) or any(g in text for g in ["hello", "good morning"]):
            return "Hello! I am your Pharmacy Assistant.\n\nI can help you Check Prices, Check Stock, Process Prescriptions, or Manage your Cart (e.g. search for a medicine and just say 'Yes' to add it).\n\nHow can I help you today?"

        # 1.5 Service Hours & Info
        if ("time" in text or "hour" in text or "open" in text or "close" in text or "when" in text or "available" in text or "pharmacist" in text or "timing" in text):
            return (
                "Here are our Service Hours:\n\n"
                "Store Hours:\n"
                "- Mon-Fri: 8:00 AM - 10:00 PM\n"
                "- Sat-Sun: 9:00 AM - 9:00 PM\n\n"
                "Pharmacist Availability:\n"
                "- Mon-Fri: 9:00 AM - 6:00 PM\n"
                "- Sat: 10:00 AM - 4:00 PM"
            )
        
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
                # Reset pending quantity
                self.sessions[session_id]["pending_quantity"] = 1

            # Extract Quantity from Search Query (e.g. "5 boxes of ibuprofen")
            search_qty = 1
            words = text.split()
            qty_map = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
            for w in words:
                if w.isdigit():
                    search_qty = int(w)
                    break
                if w in qty_map:
                    search_qty = qty_map[w]
                    break
            
            if session_id:
                 self.sessions[session_id]["pending_quantity"] = search_qty

            found_medicines = self.find_medicines(text)
            
            found_medicines = [m for m in found_medicines if not m.name.lower().startswith("test")]
            
            if found_medicines:
                if session_id:
                    self.sessions[session_id]["last_search"] = found_medicines
                
                response = "We have this in store:\n\n"
                for p in found_medicines[:5]: 
                    response += f"- **{p.name}** (${p.price})\n"
                
                response += "\nWould you like to add this to your cart?"
                return response
            else:
                return "Sorry, we don't have that medicine in our store at the moment."



        # 3. View Cart Intent
        # "What is in my cart", "show cart", "view cart"
        # 3. View Cart Intent
        # "What is in my cart", "show cart", "view cart", or just "cart" / "my cart"
        # We assume if the user just says "cart", they want to see it.
        is_view_cart = False
        if "cart" in text:
             if any(x in text for x in ["what", "show", "view", "check", "in my"]):
                 is_view_cart = True
             elif len(text.split()) <= 2: # "cart", "my cart"
                 is_view_cart = True
                 
        if is_view_cart:
            from store.models import CartItem
            
            cart_items = []
            if user_id:
                cart_items = CartItem.objects.filter(user_id=user_id)
            elif session_id:
                cart_items = CartItem.objects.filter(session_id=session_id)
            else:
                cart_items = CartItem.objects.filter(session_id__isnull=True)
            
            if not cart_items.exists():
                return "Your cart is currently empty. 🛒"
            
            msg = "Here is what you have in your cart:\n\n"
            total = 0
            for item in cart_items:
                item_total = item.get_total_price()
                total += item_total
                msg += f"- {item.quantity} x {item.medicine.name} (${item_total:.2f})\n"
            
            msg += f"\n**Total: ${total:.2f}**\n\n"
            msg += "[ Checkout Now ](/checkout/)"
            return msg

        return "I am not sure I understood that. You can ask me to check prices, find medicines, or add items to your cart. How can I help?"

    def add_to_cart_direct(self, medicine, quantity=1, session_id=None, user_id=None) -> str:
        from store.models import CartItem
        # Filter by session_id
        if user_id:
             item, created = CartItem.objects.get_or_create(medicine=medicine, user_id=user_id)
        elif session_id:
            item, created = CartItem.objects.get_or_create(medicine=medicine, session_id=session_id)
        else:
            # Fallback for legacy global behavior (shouldn't happen ideally)
            item, created = CartItem.objects.get_or_create(medicine=medicine, session_id__isnull=True)
            
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()
        
        if session_id:
            if session_id not in self.sessions: self.sessions[session_id] = {}
            self.sessions[session_id]["last_search"] = [] 
            self.sessions[session_id]["last_added"] = medicine
        
        # Calculate Total for THIS SESSION
        # Calculate Total for THIS SESSION
        if user_id:
             cart_Total = sum(i.get_total_price() for i in CartItem.objects.filter(user_id=user_id))
        elif session_id:
            cart_Total = sum(i.get_total_price() for i in CartItem.objects.filter(session_id=session_id))
        else:
            cart_Total = sum(i.get_total_price() for i in CartItem.objects.filter(session_id__isnull=True))
             
        return f"{quantity} x {medicine.name} added to your cart.\n\nItem Price: ${medicine.price * quantity:.2f}\nCurrent Cart Total: ${cart_Total:.2f}"

    def manage_cart(self, text: str, action: str, session_id: str = None, user_id: int = None) -> str:
        from store.models import CartItem, Medicine 
        
        words = text.split()
        quantity = 0 
        explicit_qty = False
        qty_map = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
        
        for w in words:
            if w.isdigit():
                quantity = int(w)
                explicit_qty = True
                break
            if w in qty_map:
                quantity = qty_map[w]
                explicit_qty = True
                break
        
        if not explicit_qty:
            quantity = 1
                
        medicines = Medicine.objects.all()
        target_med = None
        # Sort by length to match "Panadol Extra" before "Panadol"
        all_medicines = sorted(list(medicines), key=lambda x: len(x.name), reverse=True)
        
        for med in all_medicines:
             # Space-padded check to avoid partial matches like "Pan" in "Panadol"
             # But simplistic 'in' check is okay if sorted by length
            if med.name.lower() in text:
                target_med = med
                break
        
        if not target_med and action == "remove":
             if session_id and session_id in self.sessions:
                 target_med = self.sessions[session_id].get("last_added")
        
        if not target_med:
             return "I couldn't identify the medicine name to available. Please say the exact product name, e.g., 'Add Panadol to cart'."

        if action == "add":
            if user_id:
                item, created = CartItem.objects.get_or_create(medicine=target_med, user_id=user_id)
            elif session_id:
                item, created = CartItem.objects.get_or_create(medicine=target_med, session_id=session_id)
            else:
                item, created = CartItem.objects.get_or_create(medicine=target_med, session_id__isnull=True)
                
            if not created:
                item.quantity += quantity
            else:
                item.quantity = quantity
            item.save()
            
            if session_id:
                if session_id not in self.sessions: self.sessions[session_id] = {}
                self.sessions[session_id]["last_search"] = []
                self.sessions[session_id]["last_added"] = target_med
            
            if user_id:
                cart_total = sum(i.get_total_price() for i in CartItem.objects.filter(user_id=user_id))
            elif session_id:
                cart_total = sum(i.get_total_price() for i in CartItem.objects.filter(session_id=session_id))
            else:
                cart_total = sum(i.get_total_price() for i in CartItem.objects.filter(session_id__isnull=True))
                
            return f"{quantity} x {target_med.name} added to your cart.\n\nItem Price: ${target_med.price * quantity:.2f}\nCurrent Cart Total: ${cart_total:.2f}"
            
        elif action == "remove":
            try:
                if user_id:
                     item = CartItem.objects.get(medicine=target_med, user_id=user_id)
                elif session_id:
                    item = CartItem.objects.get(medicine=target_med, session_id=session_id)
                else:
                    item = CartItem.objects.get(medicine=target_med, session_id__isnull=True)
                
                # Logic: If user specified a quantity (e.g. "remove 2") and it's less than what's in cart, decrement.
                if explicit_qty and quantity < item.quantity:
                     item.quantity -= quantity
                     item.save()
                     
                     if user_id:
                         cart_total = sum(i.get_total_price() for i in CartItem.objects.filter(user_id=user_id))
                     elif session_id:
                         cart_total = sum(i.get_total_price() for i in CartItem.objects.filter(session_id=session_id))
                     else:
                         cart_total = sum(i.get_total_price() for i in CartItem.objects.filter(session_id__isnull=True))
                         
                     return f"Removed {quantity} x {target_med.name} from your cart.\nRemaining: {item.quantity}\nCurrent Cart Total: ${cart_total:.2f}"
                else:
                    item.delete()
                    
                    if session_id and session_id in self.sessions:
                        if self.sessions[session_id].get("last_added") == target_med:
                             self.sessions[session_id]["last_added"] = None
    
                    return f"{target_med.name} removed from your cart."
            except CartItem.DoesNotExist:
                return f"{target_med.name} is not in your cart."
                
        return "I didn't understand that cart command."

    def process_prescription(self, filename: str, content: bytes, session_id: str = None) -> dict:
        filename = filename.lower()
        
        # Try to decode content as text (assuming these are dummy text-based PDFs for the demo)
        try:
            text_content = content.decode('utf-8', errors='ignore').lower()
        except:
            text_content = ""
            
        all_medicines = list(Medicine.objects.all())
        found_meds = []
        
        # 1. Exact Name / Alias Matching in text_content
        # We iterate over all medicines and check if their name appears in the file
        for med in all_medicines:
            # Check Name
            if med.name.lower() in text_content:
                if med not in found_meds:
                    found_meds.append(med)
            
            # Check Aliases (Optional, but good for "Tylenol" -> Paracetamol)
            # In a real app, we'd have a reverse alias map. For now, we rely on the PharmacyBot's simple alias map if needed,
            # but simplest is just checking the DB names.
            
        # 2. Fallback: Check filename if text content turned up nothing (e.g. valid "image" but we rely on filename for demo)
        if not found_meds:
            for med in all_medicines:
                if med.name.lower() in filename:
                     if med not in found_meds:
                        found_meds.append(med)

        # 3. Construct Response
        if not found_meds:
             msg = "We analyzed your prescription, but we currently do not have the prescribed medicines in stock (or could not read the file)."
             return {
                 "message": msg,
                 "products": []
             }
        
        # Update Session Context
        if session_id:
            if session_id not in self.sessions:
                self.sessions[session_id] = {}
            self.sessions[session_id]["last_search"] = found_meds
            self.sessions[session_id]["pending_quantity"] = 1
            
        results = []
        for p in found_meds:
            results.append({
                "id": p.id,
                "name": p.name,
                "price": str(p.price),
                "image_url": p.image.url if p.image else "",
                "description": p.description[:100] + "..."
            })
            
        msg = "Prescription Analyzed\n\n"
        msg += "We found the following medicines from your prescription in our store:\n\n"
        for p in found_meds:
             msg += f"- {p.name} (${p.price})\n"
        
        msg += "\nWould you like to add these to your cart? (Type 'Yes' or 'Add all')"

        return {
            "message": msg,
            "products": results
        }
