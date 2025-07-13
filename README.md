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
- REST API for transcript requests (Django REST Framework)
- In-browser PDF preview for transcripts (user & admin dashboards)
- Automated email reminders for pending payments
- Full request timeline/history (status & comments)
- Audit trail for all admin actions
- Bulk admin actions (PDF ZIP download, notifications)
- Accessible, mobile-friendly UI (Bootstrap 5)

## New Features (July 2025)

- Student dashboard: Filter transcript requests by status (pending, ready, delivered, etc.).
- Admin dashboard: Advanced filtering and search (by status, student username/email, and date range).
- Notifications: Mark all as read with one click.
- Dashboards: Modern Bootstrap 5 cards, summaries, and recent activity for both students and admins.
- **API:** Access your transcript requests via `/transcripts/api/` (see code for details; authentication required).
- **PDF Preview:** View transcript PDFs in-browser before downloading.
- **Reminders:** Automated email reminders for pending payments.
- **Timeline:** See full request history and status changes.
- **Audit Trail:** All admin actions are logged for security.
- **Bulk Actions:** Download multiple PDFs as ZIP, send notifications, and more.
- **PWA:** Installable on mobile/desktop, works offline, and supports add-to-home-screen.
- **Accessibility:** Improved mobile and accessibility support.

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
