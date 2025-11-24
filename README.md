# 💊 MedPlus – Online Pharmacy

MedPlus is a **Django-based e-commerce platform** for buying medicines online.  
It provides a smooth user experience: browsing medicines, adding products to a cart, secure checkout, and Google social login.

---

## 🧭 Overview

MedPlus allows users to:

- Register and login with email/password
- Login via Google account
- Browse medicines by category
- Search and view product details
- Add products to the shopping cart and manage it
- Checkout with order summary
- Receive email notifications for orders (optional)
- Enjoy a responsive design optimized for desktop and mobile devices

---

## 🚀 Features

- **User Authentication** — Email/password login & Google social login  
- **Product Browsing** — View medicines by category and search  
- **Shopping Cart** — Add, update, or remove products  
- **Checkout** — View order summary and complete purchases  
- **Email Notifications** — Optional, for order confirmation  
- **Responsive Design** — Built with Bootstrap for all screen sizes  

---

## 🎥 Demo Video

Watch the demo video showing the full workflow:  
👉 [Watch on YouTube](https://www.youtube.com/watch?v=EB5bOYivwFg)

---

## ⚙️ Installation & Setup

Follow these steps to run MedPlus locally.

---

### 1️⃣ Clone the Repository

**Terminal / PowerShell:**

```bash
git clone https://github.com/zuh2407/pharmacy_app.git
cd pharmacy_app
````

**VS Code:**

1. Open VS Code → `Ctrl + Shift + P` → `Git: Clone`
2. Paste the repo link → choose folder
3. VS Code opens the project automatically

---

### 2️⃣ Create & Activate Virtual Environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in the terminal if activation succeeded.

---

### 3️⃣ Generate `requirements.txt` (Optional but Recommended)

If you don’t have `requirements.txt`, you can create it from your current environment:

```bash
pip freeze > requirements.txt
```

This will save **all installed Python packages** with exact versions to `requirements.txt`.

You can also copy and paste the package list below into `requirements.txt` if you prefer.

---

### 4️⃣ Install Dependencies

Install all required packages at once:

```bash
pip install -r requirements.txt
```

#### Full list of dependencies:

```
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

---

### 5️⃣ Configure Environment Variables

Copy `.env.example` to `.env`:

**Windows:**

```powershell
copy .env.example .env
```

**macOS / Linux:**

```bash
cp .env.example .env
```

Open `.env` and fill in credentials (optional for basic usage):

```dotenv
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_SITE_ID=1
DJANGO_TIME_ZONE=UTC

DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Optional: Email for order notifications
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Optional: Google OAuth for social login
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Optional: Stripe test keys for payments
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key

ACCOUNT_EMAIL_VERIFICATION=none
```

> `.env` contains real credentials. `.env.example` is safe for GitHub.

---

### 6️⃣ Apply Database Migrations

```bash
python manage.py migrate
```

---

### 7️⃣ (Optional) Create Admin User

```bash
python manage.py createsuperuser
```

---

### 8️⃣ Run Development Server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

**Optional — mobile access on same Wi-Fi:**

```bash
python manage.py runserver 0.0.0.0:8000
```

Open `http://<PC_IP>:8000` on your phone.

---

## 🧑‍🤝‍🧑 Collaborator Workflow

1. Accept GitHub invite
2. Clone repository
3. Create & activate virtual environment
4. Install dependencies
5. Copy `.env.example → .env` and fill credentials (optional)
6. Run migrations → `python manage.py migrate`
7. Create superuser (optional)
8. Run server → test locally
9. Open browser → [http://127.0.0.1:8000](http://127.0.0.1:8000)
10. Push changes via feature branch → open Pull Request

---

## 💻 VS Code Setup (Recommended)

* Open project in VS Code (`code .`)
* Open integrated terminal (`Ctrl + ~`)
* Activate `.venv`
* Install dependencies
* Run server (`python manage.py runserver`)
* Ctrl + Click link in terminal to open browser
* Select interpreter: `Ctrl + Shift + P` → `Python: Select Interpreter` → choose `.venv`

---

## 📂 Folder Structure

```
pharmacy_app/
│
├─ pharmacy/          # Django project
├─ store/             # Django app
├─ templates/         # HTML templates
├─ staticfiles/       # CSS, JS, images
│   └─ images/        # auth-illustration.png
├─ .env.example       # Environment variable placeholders
├─ requirements.txt
├─ README.md
└─ db.sqlite3         # Optional, ignored in GitHub
```

---

## 🤝 Contributing

1. Fork repository
2. Create branch → make changes
3. Commit → push
4. Open Pull Request

---

## ⚖️ License

MIT License © 2025 MedPlus

---

## 🧩 Notes — Generating Credentials

* **Email App Password:** [Gmail App Passwords](https://myaccount.google.com/apppasswords) (2-Step Verification required)
* **Stripe Test Keys:** [Stripe Dashboard](https://dashboard.stripe.com/test/apikeys)
* **Google OAuth:** [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
  Redirect URI: `http://127.0.0.1:8000/accounts/google/login/callback/`





