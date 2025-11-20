# import time 
# import logging
   
# from portfolio.redis_client import redis_async_client
# from channels.generic.websocket import AsyncJsonWebsocketConsumer
# from channels.db import database_sync_to_async
# from django.contrib.auth import get_user_model
# from django.utils.timezone import now
# from chats.models import Message, Chat
# from portfolio.constants import ONLINE_USERS_KEY, USER_CHANNEL_PREFIX, ONLINE_USER_EXP_TIMEOUT
# # from django.core.cache import cache

# logger = logging.getLogger(__name__)
# User = get_user_model()

# class UserConsumer(AsyncJsonWebsocketConsumer):
#     async def connect(self):
#         user = self.scope["user"]
#         if not user.is_authenticated:
#             await self.close()
#             return
        
#         self.user = user
#         self.user_id = str(self.user.id)
#         self.last_ping_time = 0
#         self.channel_key = f'{USER_CHANNEL_PREFIX}{self.user_id}'
#         self.user_presence_room = "presence_update"
        
#         await self.accept()

#         try:
#             await redis_async_client.sadd(self.channel_key, self.channel_name)
#             await redis_async_client.expire(self.channel_key, ONLINE_USER_EXP_TIMEOUT)
#             await redis_async_client.zadd(ONLINE_USERS_KEY, {str(self.user_id): int(time.time())})

#             if self.user.is_staff:
#                 await redis_async_client.zadd(ONLINE_USERS_KEY, {str(self.user_id): int(time.time())})

#         except Exception as e:
#             logger.exception("user state error", exc_info=e)

#             try:
#                 await self.channel_layer.group_add(self.user_presence_room, self.channel_name)

#                 # if user is staff brodacase online state to regular users
#                 if self.user.is_staff:
#                     await self.channel_layer.group_send(
#                         self.user_presence_room,
#                         {
#                             "type": "presence_message",
#                             "is_admin_online": True,
#                         }
#                     )
#                 else:
#                     await self.channel_layer.group_send(
#                         self.user_presence_room,
#                         {
#                             "type": "presence_message",
#                             "user_id": self.user_id,
#                             "status": "online"
#                         }
#                     )

#                 # universal channel to broadcast realtime updates
#                 self.private_channel = "staff" if self.user.is_staff else  self.channel_key

#                 await self.channel_layer.group_add(self.private_channel, self.channel_name)
#                 await self.send_initial_data()
#             except Exception as e:
#                 logger.exception("user state error", exc_info=e)


    
#     async def disconnect(self, code):
#         user = self.user

#         if user.is_authenticated:

#             try:
#                 await redis_async_client.srem(self.channel_key, self.channel_name)
#                 remaining = await redis_async_client.scard(self.channel_key)

#                 if remaining == 0:
#                     #user has no other active connections
#                     await redis_async_client.zrem(ONLINE_USERS_KEY, str(self.user_id))

#                     await self.set_last_seen()

#                     if self.user.is_staff:
#                         await self.channel_layer.group_send(
#                             self.user_presence_room,
#                             {
#                                 "type": "presence_message",
#                                 "is_admin_online": False
#                             }
#                         )
#                     else:
#                         await self.channel_layer.group_send(
#                             self.user_presence_room,
#                             {
#                                 "type": "presence_message",
#                                 "user_id": self.user_id,
#                                 "status": "offline"
#                             }
#                         )


#             except Exception as e:
#                 logger.exception("user state error", exc_info=e)

#             await self.channel_layer.group_discard(
#                 self.user_presence_room,
#                 self.channel_name
#             )

#             await self.channel_layer.group_discard(self.private_channel, self.channel_name)
#         else:
#             self.disconnect()


#     async def receive_json(self, data):
#         data_type = data.get("type")

#         try:
#             if data_type == "ping":
#                 now = time.time()

#                 if now - self.last_ping_time > 20:
#                     self.last_ping_time = now
#                     await self.update_user_state()

#         except Exception as e:
#             logger.exception("updating user state in ping failed", exc_info=e)


#     async def send_initial_data(self):
#         try:
#             msg_count = await self.get_unread_messages()
#             online_users = await self.get_online_users()

#             return await self.send_json({
#                     "type": "initial",
#                     "msg_count": msg_count
#                 })
#         except Exception as e:
#             logger.exception("Initial data sending is failed", exc_info=e)

#             return await self.send_json({
#                     "type": "error",
#                     "message": "Cannot fetch initial message count."
#                 })
        

#     async def notify(self, event):
#         type = event.get("nt_type")

#         try:
#             if type == "new_msg":
#                 msg = event.get("msg")

#                 await self.send_json({
#                     "type": type,
#                     "content" : msg,
#                 })
#         except Exception as e:
#             logger.warning("Notify send failed", exc_info=e)


#     async def update_user_state(self):
#         await redis_async_client.expire(self.channel_key, ONLINE_USER_EXP_TIMEOUT)
#         await redis_async_client.zadd(ONLINE_USERS_KEY, {str(self.user_id): int(time.time())})


#     async def presence_message(self, event):

#         if self.user.is_staff:
#             user_id = event.get("user_id")
#             status = event.get("status")
#             data = {"user_id": user_id, "status": status}
#         else:
#             is_admin_online = event.get("is_admin_online")  
#             data = {"is_admin_online": is_admin_online}

#         try:
#             await self.send_json({
#                 "type": "presence_update",
#                 **data
#             })
#         except Exception as e:
#             logger.warning("Notify send failed", exc_info=e)


#     async def get_online_users(self): 
#         try:
#             online_ids_bytes = await redis_async_client.hkeys(ONLINE_USERS_KEY)
#             if self.user and self.user.is_staff:
#                 # get all online users ids if user is staff
#                 user_ids = [int(uid.decode()) for uid in online_ids_bytes]
#                 return {"online_users": user_ids}
#             else:
#                 # else get only admin is online
#                 is_admin_online = True if "staff" in online_ids_bytes else False 
#                 return {"is_admin_online": is_admin_online}
        
#         except Exception as e:
#             logger.warning("Notify send failed", exc_info=e)
#             return []


#     @database_sync_to_async
#     def get_unread_messages(self):
#         user = self.scope["user"]
#         try:
#             if user.is_staff:
#                 count = Message.objects.filter(read=False, sender__is_staff=False).count()
#             else:
#                 chat = Chat.objects.get(user=user)
#                 count = Message.objects.filter(
#                     chat=chat,
#                     read=False
#                 ).exclude(sender=user).count()

#             return count 
#         except Chat.DoesNotExist:
#             return 0
    
    
#     @database_sync_to_async
#     def set_last_seen(self):
#         try:
#             updated = User.objects.filter(id=self.user_id).update(last_seen=now())
#             if updated == 0:
#                 raise Exception(f"No user found with id={self.user_id}")
#         except Exception as e:
#             logger.exception(f"Failed to update last_seen for user {self.user_id}", exc_info=e)


import time
import logging
import asyncio

from portfolio.redis.redis_client import redis_async_client
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from chats.models import Message, Chat

from portfolio.redis.constants import REDIS_ONLINE_USERS_SET, REDIS_ONLINE_STAFF_SET, ALL_USERS_PRESENCE_GROUP, STAFF_PRESENCE_GROUP, STAFF_GROUP, USER_PRIVATE_GROUP_PREFIX, PRIVATE_CHANNEL_TIMEOUT, MAX_CONNECTIONS_PER_USER, CONNECT_SCRIPT, DISCONNECT_SCRIPT, PING_SCRIPT

logger = logging.getLogger(__name__)
User = get_user_model()


class UserConsumer(AsyncJsonWebsocketConsumer):
    # Handles WebSocket connections for users.
    # Tracks presence, unread messages, and delivers notifications.
    async def connect(self):
        user = self.scope["user"]
        self.is_user_authenticated = user.is_authenticated
        if not user.is_authenticated:
            print("Unauthorized user")
            await self.close(code=4001, reason="unathorized")
            return

        self._last_presence_broadcast = 0
        self._last_typing_broadcast = 0
        self.user = user
        self.is_user_staff = user.is_staff
        self.user_id = str(user.id)
        self.private_channel_key = f"{USER_PRIVATE_GROUP_PREFIX}{self.user_id}"
        self.presence_channel = ALL_USERS_PRESENCE_GROUP if self.is_user_staff else STAFF_PRESENCE_GROUP   

        # Register in Redis before accepting the connection

        redis_keys = [self.private_channel_key, REDIS_ONLINE_USERS_SET, REDIS_ONLINE_STAFF_SET]
        try:
            logger.debug(f"[connect] Starting connection for user_id={self.user_id}")
            status, is_first_connection, is_first_staff, current_connection_count = await redis_async_client.eval(
                CONNECT_SCRIPT,
                len(redis_keys),
                *redis_keys, self.channel_name, self.user_id, int(time.time()), MAX_CONNECTIONS_PER_USER, "staff" if self.is_user_staff else "regular",
                PRIVATE_CHANNEL_TIMEOUT
            )

            if status == b"limit_exceeded":
                # await self.accept()
                # await self.send_json({"type": "error", "message": "conn_limit_exceeded"})
                await self.close(code=4000, reason="conn_limit_exceeded") # connection limit exceeded code 4000
                logger.warning(f"User {self.user_id} exceeded max connections ({MAX_CONNECTIONS_PER_USER}). Connection rejected. Current connection: {current_connection_count}")
                return
            
        except Exception as e:
            logger.exception(f"[connect] Redis connection error for user_id={self.user_id}, channel={self.channel_name}", exc_info=e )
            await self.close(code=1011)  # 1011 = internal error
            return
        
        # communication channel for staff users
        if self.is_user_staff:
            await self.channel_layer.group_add(STAFF_GROUP, self.channel_name)

        await self.channel_layer.group_add(self.presence_channel, self.channel_name)
        await self.channel_layer.group_add(self.private_channel_key, self.channel_name)
        await self.accept()

        logger.warning(f"Current connection of User {self.user_id}: {current_connection_count}")

        # Broadcast online status (only if this is the first connection)
        if is_first_connection:
            await self.broadcast_presence("online", is_first_staff)
        await self.send_initial_data()

    async def disconnect(self, code):
        if not getattr(self, "user", None) or not self.is_user_authenticated:
            return
        
        redis_keys = [self.private_channel_key, REDIS_ONLINE_USERS_SET, REDIS_ONLINE_STAFF_SET]
        try:
            logger.debug(f"[disconnect] Cleaning up for user_id={self.user_id}, code={code}")

            is_last_connection, is_last_staff = await redis_async_client.eval(DISCONNECT_SCRIPT, len(redis_keys), *redis_keys, self.channel_name, self.user_id, "staff" if self.is_user_staff else "regular",)
            if is_last_connection:
                await self.broadcast_presence(status="offline")
                await self.broadcast_presence(status="offline", is_staff_status_changed=is_last_staff)
                await self.set_last_seen()
        except Exception as e:
            logger.exception(f"[disconnect] Redis disconnection error for user user_id={self.user_id}, channel={self.channel_name}", exc_info=e)

        try:
            await self.channel_layer.group_discard(self.presence_channel, self.channel_name)
            await self.channel_layer.group_discard(self.private_channel_key, self.channel_name)
            if self.is_user_staff:
                await self.channel_layer.group_discard(STAFF_GROUP, self.channel_name)
        except Exception as e:
            logger.exception(f"[disconnect] Failed to discard groups for user_id={self.user_id}", exc_info=e)


    async def receive_json(self, data):
        data_type = data.get("type")
        if data_type == "ping":
            await self.handle_ping()
        elif data_type == "typing":
            chat_id = data.get("chat_id") # which chat is currently sending this event
            chat_user_id = None

            if self.user.is_staff:
                chat_user_id = data.get("chat_user_id") # chat user(owner) required for staff typing event to send to the exact users channel
            typing = data.get("typing") # typing state [True, False]

            await self.broadcast_typing({ "typing": typing, "chat_id": chat_id, "chat_user_id": chat_user_id, })

            
    async def send_initial_data(self):
        # """Send unread messages count on connection."""
        try:
            msg_count = await self.get_unread_messages()
            online_users_data = await self.get_online_users()
            await self.send_json({"type": "initial", "msg_count": msg_count, **online_users_data})
        except Exception as e:
            logger.exception("Failed to send initial data", exc_info=e)
            await self.send_json({"type": "error", "message": "Cannot fetch initial data."})
    # MESSAGE EVENTS
    # ["new-msg", "edit-msg", "delete-msg", "read_msg" <- mark as read]
    # handles channel layers automatically in api util level


    async def handle_message(self, event):
        event_type = event.get("event_type") # ["new", "edit", "read","delete"]
        data = {"content": event.get("msg")} if event_type == "new" or event_type == "edit" else {**event.get("data")}
       
        try:
            await self.send_json({"type": f"{event_type}_msg", **data})
        except Exception as e:
            logger.warning("Messages handling failed!", exc_info=e)


    # heartbeat of websocket connection
    async def handle_ping(self):
        # Refresh expiry to keep the user online
            redis_keys = [self.private_channel_key, REDIS_ONLINE_USERS_SET]
            try:
                logger.debug(f"[handle_ping] ping is received")
                await redis_async_client.eval(
                        PING_SCRIPT,
                        len(redis_keys),
                        *redis_keys, PRIVATE_CHANNEL_TIMEOUT, self.user_id, int(time.time())
                    )
            except Exception as e:
                logger.warning(
                    f"[handle_ping] Failed to refresh presence for user_id={self.user_id}",
                    exc_info=e
                )


    async def broadcast_typing(self, payload):
        now = time.time()
        if now - getattr(self, "_last_typing_broadcast", 0) < 0.3: # e.g., limit to 3.3 events/sec
            return 
        self._last_typing_broadcast = now

        user_id = self.user.id
        chat_id = payload.get("chat_id")
        chat_user_id = payload.get("chat_user_id")
        typing = payload.get("typing")

        # set communication channel by user role
        broadcast_channel = f"{USER_PRIVATE_GROUP_PREFIX}{chat_user_id}" if self.is_user_staff else "staff" 

        data = {"admin_typing": typing} if self.is_user_staff else {"chat_id": chat_id,"user_id": user_id,"typing": typing}

        try:
            await self.channel_layer.group_send(
            broadcast_channel,
                {
                    "type": "typing_update",
                    "data": data
                },
            )
        except Exception as e:
            logger.warning("Chat typing handler failed!", exc_info=e)


    async def typing_update(self, event):
        try:
            await self.send_json({"type": "typing_update", **event['data']})
        except Exception as e:
            logger.warning(f"Failed to send typing update", exc_info=e)


    async def broadcast_presence(self, status, is_staff_status_changed=False):
        now = time.time()
        if now - getattr(self, "_last_presence_broadcast", 0) < 0.3: # e.g., limit to 3.3 events/sec
            return 
        self._last_presence_broadcast = now

        try:
            if self.is_user_staff:
                channel = STAFF_PRESENCE_GROUP
                data = {"staff_status": status}
                if is_staff_status_changed:
                    logger.debug(f"[broadcast_presence] Broadcasting {status} for user_id={self.user_id}")
                    await self.channel_layer.group_send(
                            channel,
                            {
                                "type": "presence_update",
                                "data": data,
                                
                            },
                        )
            else:
                channel = ALL_USERS_PRESENCE_GROUP
                data =  {"user_id": self.user_id, "status": status,}
                logger.debug(f"[broadcast_presence] Broadcasting {status} for user_id={self.user_id}")
                await self.channel_layer.group_send(
                        channel,
                        {
                            "type": "presence_update",
                            "data": data,
                            
                        },
                    )  
        except Exception as e:
            logger.warning(
            f"[broadcast_presence] Failed to broadcast {status} for user_id={self.user_id}",
            exc_info=e
        )


    async def presence_update(self, event):
        # This handler receives messages from the `presence` group
        try:
            await self.send_json({"type": "presence_update", **event['data']})
        except Exception as e:
            logger.warning(f"[presence_update] Failed to send presence update user_id={self.user_id} channel={self.channel_name}", exc_info=e)


    async def get_online_users(self):
        if self.is_user_staff:
            ids = await redis_async_client.zrange(REDIS_ONLINE_USERS_SET, 0, -1)
            return {"online_user_ids": [uid.decode() for uid in ids]}
        else:
            staff_count = await redis_async_client.scard(REDIS_ONLINE_STAFF_SET)
            return {"staff_status": "online" if staff_count > 0 else "offline" }


    @database_sync_to_async
    def get_unread_messages(self):
        try:
            if self.is_user_staff:
                return Message.objects.filter(read=False, sender__is_staff=False).count()
            return Message.objects.filter(chat__user=self.user, read=False).exclude(sender=self.user).count()
        except Exception as e:
            logger.error("Failed to get unread messages", exc_info=e)
            return 0


    @database_sync_to_async
    def set_last_seen(self,):
        try:
            User.objects.filter(id=int(self.user_id)).update(last_seen=now())
        except Exception as e:
            logger.error("Failed to update last_seen", exc_info=e)
