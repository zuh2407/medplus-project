class RouterModel:
    def __init__(self):
        # Pharmacy Intents (transactional, inventory)
        self.pharmacy_keywords = [
            "price", "cost", "how much", 
            "buy", "purchase", "order", "get",
            "stock", "available", "have", "do you have",
            "prescription", "store", "shop",
            "cart", "add", "remove", "basket",
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
            "how are you", "thank", "thanks", "bye", "goodbye", "help"
        ]

    def route_query(self, message: str) -> str:
        message = message.lower()
        
        # Check Small Talk first (Exact or start/end matches preferrable, but simple keyword is okay for now)
        # We use a threshold or direct match for short messages
        if any(k in message for k in self.small_talk_keywords) and len(message.split()) < 5:
            return "small_talk"
        
        # Simple keyword scoring
        pharmacy_score = sum(1 for k in self.pharmacy_keywords if k in message)
        health_score = sum(1 for k in self.health_keywords if k in message)
        
        # Default behavior
        if pharmacy_score > 0:
            return "pharmacy"
        if health_score > 0:
            return "health"
            
        # Fallback / Context aware
        if "?" in message and len(message.split()) > 3:
            return "health" # Assume questions are health related if not explicitly buying
            
        return "pharmacy" # Default to pharmacy assistant
