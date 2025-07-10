# Transcript Tower

Transcript Tower is a robust Django 5 web application for managing student transcript requests. It features user registration with email/OTP verification, a flexible transcript request workflow, Paystack and manual payment options, admin dashboard, PDF upload/delivery, notifications, and a modern Bootstrap 5 UI with a red-brown and orange-cream theme.

## Features
- User registration & verification
- Transcript request workflow (soft/printed)
- Paystack & manual payment integration
- Admin dashboard & workflow management
- PDF upload & delivery (WeasyPrint)
- Notifications & email integration (django-anymail)
- Modern, responsive UI (Bootstrap 5, crispy forms)
- Security best practices
- Unit tests & extensibility

## Setup
1. Create and activate a virtual environment:
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Configure PostgreSQL in `transcript_tower/settings.py`.
4. Run migrations:
   ```sh
   python manage.py migrate
   ```
5. Create a superuser:
   ```sh
   python manage.py createsuperuser
   ```
6. Start the server:
   ```sh
   python manage.py runserver
   ```

## Testing
Run all tests with:
```sh
python manage.py test
```

## Customization
- Update Bootstrap theme in `static/` for red-brown and orange-cream colors.
- All forms use crispy forms and Bootstrap 5.
- See code comments for extensibility tips.

---
For more, see the project documentation and code comments.
