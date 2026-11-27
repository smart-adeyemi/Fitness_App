from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from templates.models import * 
from datetime import *
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from templates.helper_functions import *
from django.core.exceptions import ObjectDoesNotExist
from random import *

FOOD_NAMES = list(Food.objects.values_list('name', flat=True))
EXERCISE_NAMES = list(Exercise.objects.values_list('name', flat=True))

#preference = user.preference  #type of message user prefers?

@shared_task
def check_up_emails():
    users = User.objects.all()
    emails_sent = 0

    for user in users:
        if user.email != "test@example.com":
            emails_sent += 1
            message = Status(user)
            send_mail(
                message["subject"],
                message["message"],
                DEFAULT_EMAIL,
                [user.email],
                fail_silently=False,
            )

    return f"Sent emails to {emails_sent} users"
    