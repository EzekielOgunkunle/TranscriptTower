# Transcript Tower

Transcript Tower is a Django web app that makes it easy for students to request, pay for, and receive their transcripts. It supports both online (Paystack) and manual payments, and gives admins a simple dashboard to manage everything.

## What’s Inside

- Easy user registration with email/OTP verification
- Request soft or printed transcripts
- Pay securely online or use manual payment
- Admin dashboard for managing requests and payments
- Upload and deliver transcripts as PDFs
- Email notifications for status updates
- Clean, responsive Bootstrap 5 design
- Security best practices built-in
- Ready for extension and customization

## New Features (July 2025)

- Student dashboard: Filter transcript requests by status (pending, ready, delivered, etc.).
- Admin dashboard: Advanced filtering and search (by status, student username/email, and date range).
- Notifications: Mark all as read with one click.
- Dashboards: Modern Bootstrap 5 cards, summaries, and recent activity for both students and admins.

---

## Getting Started

1. **Set up your environment:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Configure your database** (PostgreSQL) in `transcript_tower/settings.py`.
4. **Apply migrations:**
   ```sh
   python manage.py migrate
   ```
5. **Create an admin user:**
   ```sh
   python manage.py createsuperuser
   ```
6. **Run the server:**
   ```sh
   python manage.py runserver
   ```

## Running Tests

To run all tests:
```sh
python manage.py test
```

## Customization

- Change the Bootstrap theme in `static/` to adjust colors.
- All forms use crispy forms and Bootstrap 5 for a modern look.
- The code is well-commented for easy extension.

---

For more details, check the code and comments. If you have questions or want to contribute, feel free to open an issue or pull request!
