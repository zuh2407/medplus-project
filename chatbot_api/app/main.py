import os
import django
import re
# Trigger reload (Corpus Updated)
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
    intent = router_model.route_query(request.message)
    
    if intent == "pharmacy":
        response = pharmacy_bot.process_instruction(request.message, session_id=request.session_id)
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

@app.post("/prescription")
async def process_prescription(file: UploadFile = File(...)):
    # Retrieve content
    content = await file.read()
    filename = file.filename
    
    # Process using Pharmacy Bot
    result = pharmacy_bot.process_prescription(filename, content)
    return result
