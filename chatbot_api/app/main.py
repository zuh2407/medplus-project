import os
import django
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
        response = pharmacy_bot.process_instruction(request.message)
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
