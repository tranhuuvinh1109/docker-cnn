from django.core.mail import send_mail
from django.conf import settings
import random
# from accounts.models import User

def sendMailToDrive(email, link):
    # send email
    subject = f"Your model is here"
    message = f"Link: {link}"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)
    print("->>email sented")
    