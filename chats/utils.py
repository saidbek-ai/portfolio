import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from portfolio.redis.constants import USER_PRIVATE_GROUP_PREFIX, STAFF_GROUP

logger = logging.getLogger(__name__)


# type arg must be on of them ["new", "edit", "delete", "read"]
def msg_event(event_type, payload, receiver_id=None):
    channel_layer = get_channel_layer()
    if not channel_layer: 
        return  # Optionally log this case
 
    # Build group name based on role
    room_name = STAFF_GROUP if not receiver_id else f"{USER_PRIVATE_GROUP_PREFIX}{receiver_id}"
    data = {"msg": payload} if event_type == "new" or event_type == "edit" else {"data": payload}

    try:
        async_to_sync(channel_layer.group_send)(
            room_name,
            {
                "type": "handle_message",
                "event_type": event_type, 
                **data,
            }
        )
    except Exception as e:
        logger.error(f"WebSocket notify failed for {room_name}: {e}")


# def send_realtime_msg(chat_id, msg):
#     channel_layer = get_channel_layer()
#     if not channel_layer:
#         return

#     room_name = f"chat_{chat_id}"

#     try:
#         async_to_sync(channel_layer.group_send)(
#             room_name,
#             {
#                 "type": "send_message",
#                 "msg": msg
#             }
#         )
#     except Exception as e:
        
#         logger.error(f"WebSocket notify failed for {room_name}: {e}")

# def send_chat_events(chat_id, msg, event_type):
#     pass