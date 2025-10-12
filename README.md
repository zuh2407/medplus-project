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
