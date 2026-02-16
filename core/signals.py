from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import User

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        subject = 'Xosh keldińiz!'
        message = f'Assalawma aleykum, {instance.username}! Bizdin dukanimizga xosh kelibsiz.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [instance.email] if instance.email else []

        if recipient_list:
            try:
                send_mail(subject, message, from_email, recipient_list)
            except Exception as e:
                print(f"Email jiberilmadi: {e}")