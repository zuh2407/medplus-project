import os
import django
import re
# Trigger reload (Force Update 9)
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys

# Setup Django Context
import sys
from pathlib import Path

# Add project root to path (assuming we are running from project root or similar structure)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy.settings')
django.setup()

# Import Bots (after django setup)
from .pharmacy_bot import PharmacyBot
from .health_bot import HealthBot
from .router_model import RouterModel

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class ChatRequest(BaseModel):
    message: str
    session_id: str = None  # Optional for backward compatibility
    user_id: int = None # Add user_id to link cart items to user

# Initialize Bots
pharmacy_bot = PharmacyBot()
router_model = RouterModel()

try:
    health_bot = HealthBot()
except Exception as e:
    print(f"Failed to load HealthBot: {e}")
    health_bot = None

@app.get("/")
def read_root():
    return {"status": "ok", "service": "Pharmacy AI Backend"}

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        intent = router_model.route_query(request.message)
        
        if intent == "pharmacy":
            response = pharmacy_bot.process_instruction(request.message, session_id=request.session_id, user_id=request.user_id)
        elif intent == "small_talk":
            msg = request.message.lower()
            if any(x in msg for x in ["thank", "thx", "ty"]):
                response = "You're welcome! Let me know if you need anything else. 💊"
            elif "bye" in msg or "goodbye" in msg:
                response = "Goodbye! Stay healthy! 👋"
            elif any(x in msg for x in ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"]):
                response = "Hello! I am your AI Pharmacy Assistant. How can I help you today? 🤖"
            elif any(x in msg for x in ["super", "great", "awesome", "perfect", "cool", "nice"]):
                 response = "Glad to hear it! Let me know if you need anything else. 🌟"
            elif "how are you" in msg:
                 response = "I'm functioning perfectly, thanks for asking! 🔋 How can I help you?"
            elif any(x in msg for x in ["how is life", "how's life", "how are things", "how is it going", "hows life"]):
                 response = "Life is great in the digital world! 🌐 Ready to help you with your health needs."
            elif any(x in msg for x in ["whats up", "what's up", "wassup"]):
                 response = "Not much, just here waiting to help you find the best medicines! 💊"
            elif any(x in msg for x in ["who built", "created you", "creator", "built u", "created u"]):
                response = "I was built by a team of forward-thinking developers to make healthcare easier for you! 🚀"
            elif any(x in msg for x in ["real person", "human", "robot"]):
                response = "I am a virtual assistant, not a real person. But I'm always here to help you find medicines and health info! 🤖"
            elif any(x in msg for x in ["real person", "human", "robot"]):
                response = "I am a virtual assistant, not a real person. But I'm always here to help you find medicines and health info! 🤖"
            elif re.search(r"who\s+(?:.*\s+)?(are|r)\s+(?:.*\s+)?(you|u)", msg):
                response = "I am an AI assistant designed to help you with pharmacy products and health information."
            else:
                response = "I'm here to help! Feel free to ask about medicines or health advice."
        else:
            if health_bot:
                response = health_bot.search(request.message)
            else:
                response = "I apologize, but my health information module is currently offline."
                
        return {"response": response, "intent": intent}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"response": f"INTERNAL ERROR: {str(e)}", "intent": "error"}

from typing import Optional

@app.post("/prescription")
def process_prescription(file: UploadFile = File(...), session_id: Optional[str] = Form(None)):
    try:
        # Retrieve content
        content = file.file.read()
        filename = file.filename
        
        # Process using Pharmacy Bot
        result = pharmacy_bot.process_prescription(filename, content, session_id=session_id)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Return generic error structure used by view
        return {"products": [], "message": f"INTERNAL ERROR: {str(e)}"}
