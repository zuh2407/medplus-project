# 💊 MedPlus – Intelligent Online Pharmacy

![MedPlus Banner](https://img.shields.io/badge/MedPlus-AI%20Powered%20Pharmacy-blue?style=for-the-badge)
![Django](https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95-009688?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker)

**MedPlus** is a next-generation e-commerce pharmacy platform that combines a robust **Django e-commerce store** with an intelligent **FastAPI-powered AI Chatbot**.

It goes beyond standard shopping by providing an integrated health assistant capable of answering medical queries, checking drug interactions, and managing pharmacy inventory through natural language.

---

## 🚀 Key Features

### 🛒 E-Commerce Platform (Django)
-   **User Accounts**: Secure login via Email/Password and **Google OAuth**.
-   **Product Management**: Browse medicines by category, view detailed descriptions, and stock status.
-   **Smart Cart**: Add, update, and remove items with real-time price calculation.
-   **Checkout System**: Secure checkout flow with Stripe integration support.
-   **PDF Reports**: Automated generation of order invoices and prescriptions.
-   **Responsive Design**: Mobile-friendly interface optimized for all devices.

### 🤖 AI Health Assistant (FastAPI + NLP)
-   **Hybrid Intent Routing**: Intelligently routes user queries between "Health Advice", "Pharmacy/Shopping", and "General Chat".
-   **Medical Knowledge Base**: Answers questions about symptoms, drug usages, and side effects using a curated medical corpus.
-   **Smart Pharmacy Search**: Users can ask "Do you have Aspirin?" or "Add 2 Panadol to cart" and the bot interacts directly with the store database.
-   **Contextual Awareness**: Maintains conversation context for follow-up questions.
-   **Safety Guardrails**: strict routing ensures medical advice is cautious and redirects to professionals when necessary.

---

## 🛠️ Tech Stack

*   **Backend Frameworks**: Django 5 (Store), FastAPI (Chatbot API)
*   **Database**: SQLite (Dev) / PostgreSQL (Prod ready)
*   **AI/NLP**: Scikit-Learn (TF-IDF), NLTK, FuzzyWuzzy (String matching)
*   **Frontend**: HTML5, CSS3, Bootstrap, JavaScript
*   **Infrastructure**: Docker, Docker Compose
*   **Security**: Django Allauth, Environment Variable Management

---

## ⚙️ Installation & Setup

You can run the project **locally** (traditional) or using **Docker** (recommended for full feature parity).

### Option A: 🐳 Docker (Recommended)

Run the entire system (Django Frontend + FastAPI Backend) with a single command.

1.  **Clone the Repo**:
    ```bash
    git clone https://github.com/zuh2407/medplus-project.git
    cd medplus-project
    ```

2.  **Start Services**:
    ```bash
    docker-compose up --build
    ```

3.  **Access the App**:
    *   **Store**: [http://localhost:8000](http://localhost:8000)
    *   **Chatbot API**: [http://localhost:8001/docs](http://localhost:8001/docs)

---

### Option B: 🐍 Local Python Setup

If you prefer running without Docker, you will need two terminal instances (one for existing Django, one for the FastAPI bot).

#### 1. Setup Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.\.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

<details>
<summary>Click to view full `requirements.txt` content</summary>

```text
arabic-reshaper==3.0.0
asgiref==3.10.0
asn1crypto==1.5.1
certifi==2025.10.5
cffi==2.0.0
charset-normalizer==3.4.4
click==8.3.0
colorama==0.4.6
cryptography==46.0.3
cssselect2==0.8.0
Django==5.2.7
django-allauth==0.63.6
django-widget-tweaks==1.5.0
freetype-py==2.5.1
gunicorn==21.2.0
html5lib==1.1
idna==3.11
joblib==1.5.2
lxml==6.0.2
nltk==3.9.2
numpy==2.3.4
oscrypto==1.3.0
packaging==25.0
pandas==2.3.3
pillow==12.0.0
pycairo==1.28.0
pycparser==2.23
pyHanko==0.31.0
pyhanko-certvalidator==0.29.0
PyJWT==2.10.1
pypdf==6.1.1
python-bidi==0.6.6
python-dateutil==2.9.0.post0
python-dotenv==1.0.0
pytz==2025.2
PyYAML==6.0.3
regex==2025.9.18
reportlab==4.4.4
requests==2.32.5
rlPyCairo==0.4.0
scikit-learn==1.7.2
scipy==1.16.2
six==1.17.0
sqlparse==0.5.3
stripe==2.70.0
svglib==1.6.0
threadpoolctl==3.6.0
tinycss2==1.4.0
tqdm==4.67.1
typing_extensions==4.15.0
tzdata==2025.2
tzlocal==5.3.1
uritools==5.0.0
urllib3==2.5.0
webencodings==0.5.1
whitenoise==6.5.0
xhtml2pdf==0.2.17
```
</details>

#### 2. Configuration
Copy `.env.example` to `.env` and configure your keys (Database, Google OAuth, etc.).
```bash
cp .env.example .env
```

#### 3. Run Django (Terminal 1)
```bash
python manage.py migrate
python manage.py runserver 8000
```

#### 4. Run FastAPI Chatbot (Terminal 2)
```bash
uvicorn chatbot_api.app.main:app --reload --port 8001
```

---

## 📂 Project Structure

The project is organized into a hybrid architecture:

```
medplus-project/
├── pharmacy/           # Django Project Config
├── store/              # Django App (E-commerce Logic)
├── chatbot_api/        # FastAPI App (AI Logic)
│   ├── app/            # Bot logic (endpoints, models)
│   └── scripts/        # NLP training & verification scripts
├── templates/          # HTML Templates
├── static/             # Static Assets (CSS, JS)
├── docker-compose.yml  # Container Orchestration
└── manage.py           # Django CLI
```

---

## 🤝 Contributing

1.  Fork the repository
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
