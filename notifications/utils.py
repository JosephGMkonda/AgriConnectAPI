from .models import Notification

def create_notification(recipient, sender, notif_type, message, link=None):
    if recipient != sender:  
        Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notif_type=notif_type,
            message=message,
            link=link
        )
