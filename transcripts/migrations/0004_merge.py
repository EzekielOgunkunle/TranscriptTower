# Merge migration for transcripts app
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('transcripts', '0002_transcriptrequest_price'),
        ('transcripts', '0003_notification'),
    ]

    operations = []
