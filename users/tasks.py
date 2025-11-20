import logging
from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils.timezone import now, make_aware
from django.contrib.auth import get_user_model
from portfolio.redis.redis_client import redis_sync_client
from portfolio.redis.constants import (
    REDIS_ONLINE_STAFF_SET,
    REDIS_ONLINE_USERS_SET,
    USER_PRIVATE_GROUP_PREFIX,
    STAFF_GROUP,
    ALL_USERS_PRESENCE_GROUP,
    STAFF_PRESENCE_GROUP,
    CLEAN_UP_SCRIPT,
)

logger = logging.getLogger(__name__)
User = get_user_model()
channel_layer = get_channel_layer()

def get_offline_users_data(cutoff):
    
    redis_keys= [REDIS_ONLINE_STAFF_SET,REDIS_ONLINE_USERS_SET,USER_PRIVATE_GROUP_PREFIX,]
    try:
        return redis_sync_client.eval(
            CLEAN_UP_SCRIPT,
            len(redis_keys),
            *redis_keys, 
            cutoff,
        )
    except Exception as e:
        logger.error(f"Error executing Redis cleanup script: {e}")
        return []

def process_offline_user_data(data):
    """Processes user data and prepares it for bulk updates and channel discards."""
    users_to_update = []
    user_ids = {item[0].decode() for item in data}
    users_dict = {
        str(user.id): user
        for user in User.objects.filter(id__in=list(user_ids))
    }

    for item in data:
        user_id = item[0].decode()
        if user_id in users_dict:
            user = users_dict[user_id]
            user.last_seen = make_aware(item[1])
            users_to_update.append(user)

        is_staff = int(item[2])
        is_last_staff = int(item[3])
        channels = [ch.decode() for ch in item[4:]]

        for ch in channels:
            discard_channel_groups(channel_layer, user_id, ch, is_staff)

        if is_staff and is_last_staff:
            async_to_sync(channel_layer.group_send)(
                STAFF_PRESENCE_GROUP,
                {"type": "broadcast_presence", "status": "offline", "is_staff_status_changed": True},
            )
    return users_to_update

def discard_channel_groups(channel_layer, user_id, channel, is_staff):

    async_to_sync(channel_layer.group_discard)(ALL_USERS_PRESENCE_GROUP, channel)
    async_to_sync(channel_layer.group_discard)(STAFF_PRESENCE_GROUP, channel)
    async_to_sync(channel_layer.group_discard)(f"{USER_PRIVATE_GROUP_PREFIX}{user_id}", channel)
    if is_staff:
        async_to_sync(channel_layer.group_discard)(STAFF_GROUP, channel)

@shared_task
def clean_offline_users():
    
    online_users = redis_sync_client.zcard(ALL_USERS_PRESENCE_GROUP)
    # online_user = redis_sync_client.scard("user_1")  


    if not online_users:
        logger.info("No online users to clean up.")
        return

    cutoff = int(now().timestamp()) - 60
    clean_up_data = get_offline_users_data(cutoff)
    if not clean_up_data:
        logger.info("No users found to be offline.")
        return

    users_to_update = process_offline_user_data(clean_up_data)
    if users_to_update:
        User.objects.bulk_update(users_to_update, ["last_seen"])
        logger.info(f"Updated 'last_seen' for {len(users_to_update)} users.")


# @shared_task
# def clean_offline_users():
    
#     online_users = redis_sync_client.zcard(ALL_USERS_PRESENCE_GROUP)
#     online_user = redis_sync_client.scard("user_1")
#     # print(online_users)
#     print(online_user)
#     if not online_users:
#         logger.info("No online users to clean up.")
#         return
    
    
#     print("Cleaning up")
#     return

    # cutoff = int(now().timestamp()) - 60
    # clean_up_data = get_offline_users_data(cutoff)
    # if not clean_up_data:
    #     logger.info("No users found to be offline.")
    #     return

    # users_to_update = process_offline_user_data(clean_up_data)
    # if users_to_update:
    #     User.objects.bulk_update(users_to_update, ["last_seen"])
    #     logger.info(f"Updated 'last_seen' for {len(users_to_update)} users.")


# @shared_task
# def clean_offline_users():
#     current_ts = int(now().timestamp())
#     user_ids = redis_sync_client.zrange(ONLINE_USERS_KEY, 0, -1, withscores=True)      

#     print(user_ids)
   
#     for user_id_bytes, last_activity, in user_ids:
#         user_id= user_id_bytes.decode() if isinstance(user_id_bytes, bytes) else user_id_bytes
#         key = f"{USER_CHANNEL_PREFIX}{user_id}"
#         print(key)

#         is_connected = redis_sync_client.scard(key) > 0
#         inactive_too_long = current_ts - last_activity > ONLINE_USER_EXP_TIMEOUT

#         user = User.objects.filter(id=user_id)

#         if inactive_too_long and is_connected:
#             if user.exists():
#                 dt = datetime.datetime.fromtimestamp(last_activity)

#                 if not is_aware(dt):
#                     dt = make_aware(dt)

#                 user.update(last_seen = dt)
#                 # Clean from Redis
#                 redis_sync_client.zrem(ONLINE_USERS_KEY, user_id)
#                 redis_sync_client.delete(key)