import os
import json
import re
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

class HealthBot:
    def __init__(self):
        self.model_name = 'all-MiniLM-L6-v2'
        print(f"Loading HealthBot model: {self.model_name}...")
        self.model = SentenceTransformer(self.model_name)
        
        # Paths
        self.corpus_path = os.path.join(os.path.dirname(__file__), '../corpus/cleaned/health_data.json')
        self.index_path = os.path.join(os.path.dirname(__file__), '../embeddings/faiss_index.bin')
        
        # Synonym Mapping
        self.synonyms = {
            "panadol": "acetaminophen",
            "paracetamol": "acetaminophen",
            "tylenol": "acetaminophen",
            "advil": "ibuprofen",
            "motrin": "ibuprofen",
            "aleve": "naproxen",
            "aspirin": "aspirin",
            "brufen": "ibuprofen",
            "voltarol": "diclofenac",
            "voltaren": "diclofenac"
        }

        self.documents = []
        self.index = None
        self.generic_lookup = {}
        
        self._initialize_resources()

    def _initialize_resources(self):
        # 1. Load Corpus
        if os.path.exists(self.corpus_path):
             with open(self.corpus_path, 'r', encoding='utf-8') as f:
                 self.documents = json.load(f)
             print(f"Loaded {len(self.documents)} documents from corpus.")
             
             # Build generic lookup for keyword boosting
             for idx, doc in enumerate(self.documents):
                 # Assume format "**Drug Info for NAME**"
                 match = re.search(r'\*\*Drug Info for (.*?)\*\*', doc.get('text', ''))
                 if match:
                     name = match.group(1).lower().strip()
                     self.generic_lookup[name] = idx
                     
        else:
            print("Warning: Corpus file not found.")
            return

        # 2. Check Loop: Rebuild Index if needed
        rebuild = False
        if not os.path.exists(self.index_path):
            rebuild = True
        elif os.path.exists(self.corpus_path):
             # Ensure index is newer than corpus
             if os.path.getmtime(self.corpus_path) > os.path.getmtime(self.index_path):
                 print("Corpus is newer than index. Rebuilding...")
                 rebuild = True
        
        if rebuild:
            self._build_index()
        
        # 3. Load Index
        if os.path.exists(self.index_path):
            print("Loading FAISS index...")
            self.index = faiss.read_index(self.index_path)
        else:
            print("Error: FAISS index could not be created or loaded.")

    def _build_index(self):
        print("Building FAISS index...")
        texts = [doc['text'] for doc in self.documents]
        embeddings = self.model.encode(texts)
        
        # Initialize FAISS
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(embeddings).astype('float32'))
        
        # Save
        # Ensure dir exists
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(index, self.index_path)
        print("FAISS index built and saved.")

    def _preprocess_query(self, query: str) -> str:
        """Replace brand names with generics to improve search relevance."""
        words = query.lower().split()
        new_words = []
        for word in words:
            # Simple fuzzy-ish check or direct map
            # Strip punctuation
            clean_word = word.strip("?!.,")
            if clean_word in self.synonyms:
                new_words.append(self.synonyms[clean_word])
            else:
                new_words.append(word)
        return " ".join(new_words)

    def _to_bullet_points(self, text: str, section_name: str = "") -> str:
        """Convert paragraph text into a clean bulleted list."""
        if not text or text == "Information not available.":
            return "Information not available."

        # 1. Clean up common artifacts using Regex
        # Remove "1 INDICATIONS AND USAGE" type headers
        text = re.sub(r'\d+\s+INDICATIONS\s+AND\s+USAGE', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\d+\s+DOSAGE\s+AND\s+ADMINISTRATION', '', text, flags=re.IGNORECASE)
        
        # Remove parenthetical references like ( 1.1 ) or ( 2.2, 2.6 ) or [see Warnings...]
        # Catches ( 1.1 ) and ( 1.2 , 3.4 )
        text = re.sub(r'\(\s*[\d\.\s,]+\s*\)', '', text)
        text = re.sub(r'\[see.*?\]', '', text, flags=re.IGNORECASE)
        
        # Remove "Limitations of Use:" labels if they are inline
        text = text.replace('Limitations of Use:', '')

        # Handle embedded section headers like "2.1 Recommended Dosage" found in run-on text.
        # We replace them with a generic split marker to force a new bullet later.
        # Pattern: digits.digits Space CapitalLetter
        text = re.sub(r'(\d+\.\d+\s+[A-Z])', r'. \1', text) 
        
        # Handle inline numbering like "1) item 2) item" or "1. item 2. item"
        # We replace them with ". " so the splitter below treats them as new sentences/bullets
        text = re.sub(r'\s\d+[\)\.]\s', '. ', text)

        # CLEANUP: Remove redundant section name at start if present
        # e.g. "Uses temporarily relieves..." (Section is Indications/Uses)
        # e.g. "Warnings Liver warning..."
        if section_name:
            # Flexible match for common starts
            # For Indications: remove "Uses"
            if section_name == "Indications":
                 text = re.sub(r'^Uses\s+', '', text.strip(), flags=re.IGNORECASE)
            # For others: remove exact section name
            elif section_name == "Warnings":
                 text = re.sub(r'^Warnings\s+', '', text.strip(), flags=re.IGNORECASE)
            elif section_name == "Dosage":
                 text = re.sub(r'^Directions\s+', '', text.strip(), flags=re.IGNORECASE)

        # 2. Split by common delimiters (periods, semicolons). 
        # We look for periods that end a sentence (followed by space or end of string)
        chunks = re.split(r'[.;]\s+', text)
        
        # 3. Filter and format
        bullets = []
        seen = set() # Dedup lines
        for chunk in chunks:
            clean_chunk = chunk.strip()
            # Remove leading numbers/bullets if present (e.g. "1. " or "• ")
            clean_chunk = re.sub(r'^[\d\.\-\u2022]+\s*', '', clean_chunk)
            
            if clean_chunk and len(clean_chunk) > 3: # Skip tiny fragments
                # Dedup
                if clean_chunk.lower() in seen:
                    continue
                seen.add(clean_chunk.lower())
                
                # Capitalize first letter
                clean_chunk = clean_chunk[0].upper() + clean_chunk[1:]
                # Remove trailing period
                if clean_chunk.endswith('.'):
                    clean_chunk = clean_chunk[:-1]
                    
                bullets.append(f"- {clean_chunk}")
        
        return "\n".join(bullets)

    def _smart_format(self, raw_text: str, query_brand: str = None) -> str:
        """Parse raw text into structured, concise sections with headers and bullets."""
        # 1. Extract Drug Name
        title_match = re.search(r'\*\*Drug Info for (.*?)\*\*', raw_text)
        generic_name = title_match.group(1) if title_match else "Medicine"
        
        # Display Title Logic: "Panadol (Acetaminophen)" or just "Acetaminophen"
        if query_brand and query_brand.lower() != generic_name.lower() and query_brand.lower() not in generic_name.lower():
             display_title = f"{query_brand.title()} (same as {generic_name})"
        else:
             display_title = generic_name

        # 2. Extract Sections
        # We need flexible lookaheads because sections might appear in any order or be missing
        # Common keys in FDA labels: Indications, Dosage, Contraindications, Warnings, Adverse Reactions, Drug Interactions
        patterns = {
            "Indications": r'\*\*Indications:\*\*(.*?)(?=\*\*Dosage:|\*\*Contraindications:|\*\*Warnings:|\*\*Drug Interactions:|$)',
            "Dosage": r'\*\*Dosage:\*\*(.*?)(?=\*\*Contraindications:|\*\*Warnings:|\*\*Drug Interactions:|$)',
            "Contraindications": r'\*\*Contraindications:\*\*(.*?)(?=\*\*Warnings:|\*\*Drug Interactions:|\*\*Dosage:|$)',
            "Warnings": r'\*\*Warnings:\*\*(.*?)(?=\*\*Drug Interactions:|\*\*Dosage:|\*\*Contraindications:|$)',
            "Interactions": r'\*\*Drug Interactions:\*\*(.*?)(?=\*\*|$)'
        }
        
        sections = {}
        has_content = False
        for key, pattern in patterns.items():
            match = re.search(pattern, raw_text, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                # Convert to bullet points with section context
                sections[key] = self._to_bullet_points(content, section_name=key)
                if sections[key] != "Information not available.":
                    has_content = True
            else:
                sections[key] = "Information not available."

        # 3. Construct Clean Output
        # User requested "just drug name in bold" and no hashtags
        # We assume the Frontend chat.js handles **Bold** correctly now.
        response = f"**{display_title}**\n\n"
        
        if sections.get('Indications') and sections['Indications'] != "Information not available.":
            response += f"**✅ Uses:**\n{sections['Indications']}\n\n"

        if sections.get('Contraindications') and sections['Contraindications'] != "Information not available.":
            response += f"**⛔ Do Not Use If:**\n{sections['Contraindications']}\n\n"
            
        if sections.get('Warnings') and sections['Warnings'] != "Information not available.":
            response += f"**⚠️ Warnings:**\n{sections['Warnings']}\n\n"

        if sections.get('Interactions') and sections['Interactions'] != "Information not available.":
            response += f"**🔁 Drug/Food Interactions:**\n{sections['Interactions']}\n\n"
            
        if sections.get('Dosage') and sections['Dosage'] != "Information not available.":
            response += f"**📋 Dosage:**\n{sections['Dosage']}"
            
        # Fallback: If parsing failed to extract sections, show simplified raw text
        if not has_content:
             # Basic cleanup of formatting artifacts
             clean_text = raw_text.replace("**Indications:**", "").replace("**Warnings:**", "").replace("**Dosage:**", "").strip()
             # Truncate if huge, but usually safe to show mostly
             summary = clean_text[:600] + ("..." if len(clean_text) > 600 else "")
             response += f"**ℹ️ General Information:**\n{summary}"
        
        return response.strip()

    def search(self, query: str, top_k: int = 1):
        if not self.index or not self.documents:
            return "I'm sorry, my health knowledge base is currently unavailable."

        # 1. Preprocess Query (Synonyms)
        enhanced_query = self._preprocess_query(query)
        print(f"Original Query: {query} -> Enhanced: {enhanced_query}")
        
        # Detect if user used a brand name (simple fallback using synonyms dict keys)
        # We check split words to find the brand
        query_words = query.lower().split()
        brand_used = None
        for word in query_words:
            clean = word.strip("?!.,")
            if clean in self.synonyms:
                 brand_used = clean
                 break
        
        # 2. KEYWORD PRIORITY SEARCH
        enhanced_words = enhanced_query.lower().split()
        for word in enhanced_words:
            clean = word.strip("?!.,")
            if clean in self.generic_lookup:
                print(f"Direct Keyword Match found: {clean}")
                idx = self.generic_lookup[clean]
                doc = self.documents[idx]
                return "Here is the information I found:\n\n" + self._smart_format(doc['text'], query_brand=brand_used)

        # 3. VECTOR SEARCH
        query_vector = self.model.encode([enhanced_query])
        
        # Return only the TOP result to avoid confusion (User requested precision)
        D, I = self.index.search(np.array(query_vector).astype('float32'), top_k) 
        
        # Threshold Check for Relevance
        # If distance is too high, it means the query is likely off-topic (e.g. "Capital of France")
        # Calibrated value: Irrelevant queries ~1.8. Relevant ~0.5-0.9. Threshold set to 1.35.
        # UPDATE: Increased to 1.5 to catch "symptoms of flu" which might be marginally related to Aspirin/Acetaminophen texts
        if D[0][0] > 1.5:
            return "I'm sorry, I can only help with questions related to medicines and health conditions. 🩺"

        results = []
        for i in range(top_k):
            idx = I[0][i]
            if idx < len(self.documents):
                doc = self.documents[idx]
                formatted_text = self._smart_format(doc['text'], query_brand=brand_used)
                results.append(formatted_text)
                
        if results:
            # Check if query implies looking for condition symptoms rather than drug info
            # e.g. "symptoms of fever", "signs of flu"
            is_condition_query = re.search(r'\b(symptoms|signs|cause|what is|treat|help with|for)\b', query, re.IGNORECASE)
            
            # If asking about symptoms but we found a drug, phrase it carefully
            # If asking about symptoms but we found a drug, phrase it carefully
            if is_condition_query:
                return "Here is the information I found:\n\n" + results[0]
            else:
                return "Here is the information I found:\n\n" + results[0]
            
        return "I couldn't find relevant health information for your query."
