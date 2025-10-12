Absolutely! Here’s your **clean, ready-to-paste version** of the README.md in **plain Markdown** — no extra code blocks around it, ready to go directly into your `README.md` file:

---

# MedPlus - Online Pharmacy

MedPlus is a Django-based e-commerce platform for buying medicines online. It provides a smooth user experience, including browsing medicines, adding products to a cart, secure checkout, and Google social login.

---

## Overview

MedPlus allows users to:

* Register and login with email/password
* Login via Google account
* Browse medicines by category
* Search and view product details
* Add products to the shopping cart and manage it
* Checkout with order summary
* Receive email notifications for orders
* View a responsive UI across desktop and mobile devices

---

## Features

* **User Authentication**: Email/password login and Google social login
* **Product Browsing**: View medicines by category and search
* **Shopping Cart**: Add, update, or remove products
* **Checkout**: View order summary and complete purchases
* **Email Notifications**: Receive confirmation emails for orders
* **Responsive Design**: Mobile-friendly using Bootstrap

---

## Demo Video

Watch the demo video showing the application running locally:

[Watch Demo Video](https://youtu.be/EB5bOYivwFg)

> The video demonstrates the full application workflow: login, Google login, product browsing, cart management, checkout, and order confirmation.

---

## Installation & Setup

Follow these steps to run the project locally:

### 1. Clone the repository

```bash
git clone https://github.com/your-username/medplus.git
cd medplus
```

### 2. Create and activate a virtual environment

**Windows:**

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the root directory. Example:

```
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
ACCOUNT_EMAIL_VERIFICATION=none
```

> **Important:** Do not commit your real `.env` file. Use `.env.example` instead.

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Run the development server

```bash
python manage.py runserver
```

* Open your browser at [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to view the application.

---

## Folder Structure

```
pharmacy_app/
│
├─ pharmacy/                 # Django project folder (settings.py, wsgi.py)
├─ store/                    # Django app
├─ templates/                # HTML templates
├─ staticfiles/              # CSS, JS, images
│   └─ images/               # auth-illustration.png, etc.
├─ .env.example              # Example environment variables
├─ requirements.txt
├─ README.md
└─ db.sqlite3                # Optional: database file (ignore in GitHub)
```

---

## How to Use

1. Register a new account or login via Google
2. Browse available medicines by category
3. Add desired products to the cart
4. Checkout to complete your order
5. Check email for order confirmation (if email settings are configured)

---

## Contributing

1. Fork the repository
2. Create a branch (`git checkout -b feature/your-feature`)
3. Make changes
4. Commit (`git commit -m "Add feature"`)
5. Push (`git push origin feature/your-feature`)
6. Open a Pull Request

---

## License

MIT License

---

## Notes

* The demo video is hosted externally on YouTube to avoid GitHub file size limits.
* Ensure your `.env` file is correctly configured to run the project locally.
* You can safely remove any large local video from the repo to keep it lightweight:

```bash
git rm --cached demo/medplus-demo.mp4
git commit -m "Remove large demo video, use YouTube link instead"
git push origin main
```

---

### Next Steps

1. Replace `your-username` in the clone URL with your GitHub username.
2. Make sure `.env.example` is in the repo with placeholder values.
3. Push this README.md to your GitHub repository.

---
How a collaborator can run MedPlus locally:

Quick summary: clone the repo → create venv → install requirements → copy .env.example → fill real values → run migrations → (optionally) collect static → create superuser → runserver.

1) Clone the repository
git clone https://github.com/<your-username>/pharmacy_app.git
cd pharmacy_app


Replace <your-username> with your GitHub username.

2) Create & activate a virtual environment

Windows

python -m venv .venv
.\.venv\Scripts\activate


macOS / Linux

python3 -m venv .venv
source .venv/bin/activate


If Python is not found, they should install Python 3.10+ (3.11 recommended).

3) Update pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt


If dependency install fails, check Python version and pip output; share the error if unsure.

4) Copy .env.example to .env and fill values

Project should have a .env.example. Tell them to:

cp .env.example .env        # macOS/Linux
copy .env.example .env      # Windows (PowerShell: cp works too)


Open .env and set values:

DJANGO_SECRET_KEY=some-random-secret
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
STRIPE_PUBLIC_KEY=...
STRIPE_SECRET_KEY=...
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
ACCOUNT_EMAIL_VERIFICATION=none


Notes:

For quick local testing, DJANGO_DEBUG=True is fine.

If you don’t want to configure Google/Stripe/email, leave those fields blank — the app will still run for basic flows.

Never commit .env to GitHub.

5) Database setup & migrations

If the project uses SQLite (default), no extra DB server is needed.

Run:

python manage.py migrate


If the project uses PostgreSQL, they must set DB_ENGINE, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT in .env and have Postgres installed.

6) (Optional) Load sample data

If you have fixtures, you can load them:

python manage.py loaddata demo_fixture.json


(Only if you included a fixture file; otherwise skip.)

7) Create a superuser (admin)
python manage.py createsuperuser
# follow the prompts (username/email/password)


They can now login to /admin/.

8) Static files (development)

In development with DEBUG=True, Django serves static files automatically if STATICFILES_DIRS is configured. If you want to collect static (useful to test WhiteNoise locally):

python manage.py collectstatic --noinput


(Collectstatic writes to STATIC_ROOT.)

9) Run the development server
python manage.py runserver


Open in browser: http://127.0.0.1:8000/

If they want to show the site on a phone across the same Wi‑Fi:

Find PC IP (ipconfig on Windows, ifconfig/ip addr on mac/linux).

Run server binding all interfaces:

python manage.py runserver 0.0.0.0:8000


On phone open: http://<PC_IP>:8000/ (ensure firewall allows it).

10) Google OAuth (optional, for social login)

If they want to test Google login, they must:

Create OAuth credentials in Google Cloud Console.

Add redirect URI in Google Console:

http://127.0.0.1:8000/accounts/google/login/callback/


Put GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET into .env.

If Google login fails, check site domain in Google Console and that SOCIALACCOUNT_PROVIDERS is correctly configured.

11) Stripe (optional)

For payment flows use Stripe test keys in .env:

STRIPE_PUBLIC_KEY=pk_test_xxx
STRIPE_SECRET_KEY=sk_test_xxx


Use Stripe test cards during testing (e.g., 4242 4242 4242 4242).

12) Email for local testing

For real email notifications, fill SMTP credentials in .env.

For local testing without real SMTP, temporarily set:

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


or in .env add a flag the settings.py uses to switch to console backend.

13) Common troubleshooting & fixes

“Module not found” errors: Ensure virtualenv is activated and pip install -r requirements.txt succeeded.

Python version conflicts: Use Python 3.11 if you used packages requiring it (Django 5.x). Check python --version.

Migrations errors: Run python manage.py makemigrations then migrate. If stuck, inspect the traceback.

Static images not showing: If DEBUG=True, static served automatically. If not, run collectstatic and ensure WhiteNoise is configured.

Large file pushed earlier: If they clone the repo and LFS was used, they may need to install Git LFS: git lfs install.

Blocked port 8000: Another app uses it — run runserver 0.0.0.0:8001 or stop the conflicting app.

14) Pulling latest changes (daily workflow)

Tell them to update their copy regularly:

git pull origin main


If they create a branch for features:

git checkout -b feature/my-feature
# make changes
git add .
git commit -m "Add X"
git push origin feature/my-feature
# open PR on GitHub

15) Helpful commands summary
# clone
git clone https://github.com/<user>/pharmacy_app.git

# venv
python -m venv .venv
.\.venv\Scripts\activate   # Windows
source .venv/bin/activate  # mac/linux

# install
pip install -r requirements.txt

# env
cp .env.example .env
# edit .env

# migrate & create superuser
python manage.py migrate
python manage.py createsuperuser

# collectstatic (optional)
python manage.py collectstatic --noinput

# run server
python manage.py runserver
# or runserver 0.0.0.0:8000 to access from phone

# git workflow
git checkout -b feature/xxx
git add .
git commit -m "message"
git push origin feature/xxx