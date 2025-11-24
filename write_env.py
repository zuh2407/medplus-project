env_content = """DJANGO_SECRET_KEY=kl$qr$)k63==61mg_zhp1izy_dgn!wo4b_fstq9k=rr0y-2h&m
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,192.168.56.1
DJANGO_SITE_ID=1
DJANGO_TIME_ZONE=UTC

DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=zuhair2407atham@gmail.com
EMAIL_HOST_PASSWORD=zzqv euiv mnbf ytqe
DEFAULT_FROM_EMAIL=MedPlus <zuhair2407atham@gmail.com>

GOOGLE_CLIENT_ID=585355356819-htho1r1a90rmj0kvjvcl196gfemp0e22.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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

STRIPE_PUBLIC_KEY=pk_test_51S2CQ5HakvT0SdpWW7qfKs0Law2QCVvmXsMlicro3ROvEZU5U79VqRQzvYWkFt5bT9owvIkBeBvZmMBsSGLZcRwv004rLwRcjE
STRIPE_SECRET_KEY=sk_test_51S2CQ5HakvT0SdpW2nv9ZB9TQlwkxB23yoJ5jo7CyX5wh6201AoIN21rXtZqvAM3YQZnA7VTi3nZwPxAHB2jf05y00Lf8bXyZ3
"""

with open('.env', 'w') as f:
    f.write(env_content)
print("Written .env file")
