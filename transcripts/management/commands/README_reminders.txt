# To schedule payment reminders, add this to your crontab (runs daily at 8am):
#
# 0 8 * * * cd /home/vanessa/H.A.N.N.A.H/transbaby && /home/vanessa/H.A.N.N.A.H/transbaby/venv/bin/python manage.py send_payment_reminders
#
# Or use a task scheduler like Celery for more advanced scheduling.
