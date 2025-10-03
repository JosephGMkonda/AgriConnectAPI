from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def push_notification(notification):
    channel_layer = get_channel_layer()
    group_name = f"user_{notification.recipient.id}"
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send_notification",
            "data": {
                "id": notification.id,
                "notif_type": notification.notif_type,
                "message": notification.message,
                "sender": notification.sender.username if notification.sender else None,
                "created_at": str(notification.created_at),
            },
        },
    )
