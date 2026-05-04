# ComplainXHostel_app/utils/realtime.py

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def send_realtime(event_type, data):

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        "hostel",
        {
            "type": "send_update",
            "data": {
                "event": event_type,
                "payload": data
            }
        }
    )