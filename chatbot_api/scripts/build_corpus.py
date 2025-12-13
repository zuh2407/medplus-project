import requests
import json
import os
import time

# List of medical topics to build our "Real" Corpus
TOPICS = [
    # Common Diseases
    "Influenza", "Common cold", "COVID-19", "Diabetes mellitus", "Hypertension", 
    "Asthma", "Migraine", "Arthritis", "Gastroesophageal reflux disease", "Pneumonia",
    "Bronchitis", "Allergy", "Insomnia", "Anxiety disorder", "Depression (mood)",
    
    # Common Medications (Generic Names)
    "Paracetamol", "Ibuprofen", "Aspirin", "Amoxicillin", "Metformin", 
    "Lisinopril", "Atorvastatin", "Omeprazole", "Furosemide", "Gabapentin",
    "Metoprolol", "Losartan", "Albuterol", "Cetirizine", "Loratadine",
    
    # Vitamins & Supplements
    "Vitamin D", "Vitamin C", "Calcium", "Iron supplement", "Magnesium",
    "Zinc", "Fish oil", "Melatonin"
]

CORPUS_DIR = os.path.join(os.path.dirname(__file__), '../corpus/cleaned')
OUTPUT_FILE = os.path.join(CORPUS_DIR, 'health_data.json')

def fetch_wikipedia_summary(title):
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "id": f"wiki_{data.get('pageid')}",
                "source": "Wikipedia",
                "title": data.get('title'),
                "text": data.get('extract'),
                "url": data.get('content_urls', {}).get('desktop', {}).get('page', '')
            }
    except Exception as e:
        print(f"Error fetching Wikipedia for {title}: {e}")
    return None

def fetch_openfda_label(drug_name):
    """
    Fetches drug label information from OpenFDA (Source of DailyMed data).
    """
    try:
        # Search for the drug by generic name
        url = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:\"{drug_name}\"&limit=1"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                result = data['results'][0]
                
                # Extract useful sections
                indications = result.get('indications_and_usage', [''])[0]
                warnings = result.get('warnings', [''])[0]
                dosage = result.get('dosage_and_administration', [''])[0]
                
                # Combine into a useful text block
                full_text = f"**Drug Info for {drug_name}**\n\n**Indications:** {indications}\n\n**Warnings:** {warnings}\n\n**Dosage:** {dosage}"
                
                # Truncate if too long (some labels are massive)
                if len(full_text) > 2000:
                    full_text = full_text[:2000] + "..."
                    
                return {
                    "id": f"openfda_{drug_name}",
                    "source": "OpenFDA (DailyMed)",
                    "title": f"{drug_name} Label Information",
                    "text": full_text,
                    "url": "https://open.fda.gov/"
                }
    except Exception as e:
        print(f"Error fetching OpenFDA for {drug_name}: {e}")
    return None

def build_corpus():
    if not os.path.exists(CORPUS_DIR):
        os.makedirs(CORPUS_DIR)
        
    documents = []
    print(f"Fetching data for {len(TOPICS)} medical topics...")
    
    for topic in TOPICS:
        print(f" Processing Topic: {topic}")
        
        # 1. Try Wikipedia for ALL topics (General Knowledge)
        wiki_doc = fetch_wikipedia_summary(topic)
        if wiki_doc:
            documents.append(wiki_doc)
            
        # 2. Try OpenFDA for Medications (Deep Clinical Data)
        # Simple heuristic: if it's in our medication list part of TOPICS
        # (We'll just try for all, worst case it returns nothing)
        fda_doc = fetch_openfda_label(topic)
        if fda_doc:
            print(f"  + Found FDA Label data for {topic}")
            documents.append(fda_doc)
            
        time.sleep(0.3) # Be nice to APIs
        
    print(f"Successfully collected {len(documents)} documents from multiple sources.")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(documents, f, indent=4)
        
    print(f"Enhanced Corpus saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    build_corpus()
