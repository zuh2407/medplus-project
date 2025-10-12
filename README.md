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

👉 [Watch Demo Video on YouTube](#)

---

## ⚙️ Installation & Setup

Follow these steps to run MedPlus locally.  

### 1️⃣ Clone the Repository

**Option A — Terminal / PowerShell:**

```bash
git clone https://github.com/zuh2407/pharmacy_app.git
cd pharmacy_app
Option B — VS Code:

Open VS Code → Ctrl + Shift + P → Git: Clone

Paste the repo link → choose folder

VS Code opens the project automatically

2️⃣ Create & Activate Virtual Environment

Windows (PowerShell):

python -m venv .venv
.\.venv\Scripts\activate


macOS / Linux:

python3 -m venv .venv
source .venv/bin/activate


You should see (.venv) in the terminal if activation succeeded.

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Configure Environment Variables

Copy .env.example to .env:

Windows:

copy .env.example .env


macOS / Linux:

cp .env.example .env


Open .env and fill your own credentials (optional for basic usage):

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


Tips for generating credentials:

Gmail App Password → Gmail App Passwords

(2-Step Verification required)

Stripe Test Keys → Stripe Dashboard

Google OAuth → Google Cloud Console

Redirect URI: http://127.0.0.1:8000/accounts/google/login/callback/

.env contains real credentials. .env.example is safe for GitHub.

5️⃣ Apply Database Migrations
python manage.py migrate

6️⃣ (Optional) Create Admin User
python manage.py createsuperuser

7️⃣ Run Development Server
python manage.py runserver


Open http://127.0.0.1:8000
 in your browser.

Optional — mobile access on same Wi-Fi:

python manage.py runserver 0.0.0.0:8000


Open http://<PC_IP>:8000 on your phone.

🧑‍🤝‍🧑 Collaborator Workflow

Accept GitHub invite

Clone repository

Create & activate virtual environment

Install dependencies

Copy .env.example → .env and fill credentials (optional)

Run migrations → python manage.py migrate

Create superuser (optional)

Run server → test locally

Open browser → http://127.0.0.1:8000

Push changes via feature branch → open Pull Request

💻 VS Code Setup (Recommended)

Open project in VS Code (code .)

Open integrated terminal (Ctrl + ~)

Activate .venv

Install dependencies

Run server (python manage.py runserver)

Ctrl + Click link in terminal to open browser

Select interpreter: Ctrl + Shift + P → Python: Select Interpreter → choose .venv

📂 Folder Structure
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

🤝 Contributing

Fork repository

Create branch → make changes

Commit → push

Open Pull Request

⚖️ License

MIT License © 2025 MedPlus

🧩 Notes — Generating Credentials

Email App Password → Gmail App Passwords

Stripe API Keys → Stripe Dashboard

Google OAuth → Google Cloud Console

Redirect URI: http://127.0.0.1:8000/accounts/google/login/callback/