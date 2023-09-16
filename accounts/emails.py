from django.core.mail import send_mail
from django.conf import settings
import random
from accounts.models import User

def send_otp_via_email(email):
    # send email
    subject = f"OTP for Verification"
    otp = random.randint(1000, 9999)
    message = f"Your OTP is {otp}"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)
    user_obj = User.objects.get(email=email)
    user_obj.otp = otp
    user_obj.save()