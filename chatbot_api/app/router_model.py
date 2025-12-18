import re

class RouterModel:
    def __init__(self):
        # Pharmacy Intents (transactional, inventory)
        self.pharmacy_keywords = [
            "price", "cost", "how much", 
            "buy", "purchase", "order", "get", "need", "want", "looking for", "find", "search",
            "stock", "available", "have", "do you have", "take",
            "prescription", "store", "shop",
            "cart", "add", "remove", "basket", "medicine", "drug",
            "time", "hour", "open", "close", "when"
        ]
        
        # Health Intents (informational)
        self.health_keywords = [
            "what is", "what are", "about",
            "side effect", "symptom", "dose", "dosage",
            "treat", "cure", "usage", "use", "uses",
            "benefit", "risk", "pain", "fever", "flu",
            "warning", "warnings", "indication", "indications",
            "info", "information"
        ]
        # Small Talk Intents
        self.small_talk_keywords = [
            "hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening",
            "how are you", "thank", "thanks", "bye", "goodbye", "help", "who are you",
            "who are u", "who r u", "who r you", "thx", "ty",
            "who built", "who created", "built u", "created u",
            "super", "great", "awesome", "perfect", "cool", "nice"
        ]
        # Medical Context (Narrative/Advice seeking)
        self.medical_context_keywords = [
            "doctor", "prescribed", "taking", "feel", "feeling", 
            "dizzy", "hurt", "hurts", "sick", "pain", "ache",
            "medical", "advice", "should i", "start again", "stop taking",
            "consult", "opinion", "recommend"
        ]

    def route_query(self, message: str) -> str:
        message = message.lower()
        tokens = set(message.split())
        
        # Check Small Talk first
        # Use token matching for single words to avoid "ho" in "how" match issues
        for k in self.small_talk_keywords:
            if " " in k: # Multi-word phrase (e.g. "how are you")
                if k in message:
                    return "small_talk"
            else: # Single word (e.g. "hi")
                if k in tokens:
                    return "small_talk"
        
        # Regex Matching for Robust Phrases (Handles "who the hell are you")
        # Matches: "who ... are ... you/u"
        if re.search(r"who\s+(?:.*\s+)?(are|r)\s+(?:.*\s+)?(you|u)", message):
             return "small_talk"
             
        # Matches: "how ... (are|r) ... (you|u)"
        if re.search(r"how\s+(?:.*\s+)?(are|r)\s+(?:.*\s+)?(you|u)", message):
             return "small_talk"
        
        # Scoring
        pharmacy_score = sum(1 for k in self.pharmacy_keywords if k in message)
        health_score = sum(1 for k in self.health_keywords if k in message)
        medical_context_score = sum(1 for k in self.medical_context_keywords if k in message)
        
        # Logic: Prioritize Health/Medical Advice for narrative queries
        # If the user mentions a doctor, symptoms ("dizzy"), or asks for advice ("should I"),
        # it is a HEALTH query, even if they use words like "have" or "buy" (e.g. "Do I have to buy...").
        if medical_context_score > 0:
            return "health"
            
        # Standard comparison
        if health_score > pharmacy_score:
            return "health"
        if pharmacy_score > 0:
            return "pharmacy"
            
        # Fallback / Context aware
        if "?" in message and len(message.split()) > 3:
            return "health" # Assume questions are health related if not explicitly buying
            
        return "pharmacy" # Default to pharmacy assistant
