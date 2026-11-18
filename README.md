# BudgetBuddy: Track Your Money, Control Your Spending

Django (templates) + PostgreSQL/Supabase. Phase 1: Account Feature.

## Setup
```bash
python -m venv venv
venv\Scripts\activate          # Windows  (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env         # then fill in your database credentials
python manage.py makemigrations accounts
python manage.py migrate
python manage.py createsuperuser   # creates an Admin-role account
python manage.py runserver
```

## Roles
- **Registered User**: created through /register/. Goes to the user dashboard.
- **Admin**: created with `createsuperuser` (or by an admin in /django-admin/). Goes to the admin dashboard.

Opening the other role's dashboard URL returns 403; logged-out visitors are redirected to /login/.
