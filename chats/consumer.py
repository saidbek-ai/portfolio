import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import Chat, Message
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)
User = get_user_model()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'
        is_allowed = await self.is_chat_member_or_staff(user, self.chat_id)

        if not user.is_authenticated or not is_allowed:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()


    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    async def receive_json(self, data):
        data_type = data.get("data_type")
        chat_id = data.get("chat_id")
        res = {}

        try:
            if data_type == "read_messages":
                last_message_id = data.get("last_message_id")
                res = await self.read_messages(chat_id, last_message_id)

            elif data_type == "delete_messages":
                deleted_msgs = data.get("deleted_msgs_ids")
                res = await self.delete_messages(chat_id, deleted_msgs)
                
            elif data_type == "update_message":
                msg_id = data.get("msg_id")
                text_content = data.get("text_content")

                res = await self.update_message(chat_id, msg_id, text_content)

            else:
                res = {"error": "Invalid data_type", "code": 400, "close": True}

            if res.get("close"):
                await self.close()
            await self.send_json({**res})

        except Exception as e:
            logger.exception("Unexpected error in receive_json", exc_info=e)
            await self.send_json({"type": "error", "message": "Internal server error"})
            await self.close()
        

    async def send_message(self, event):
        new_message = event.get("msg")
        await self.send_json({"type": "new_message","new_message": new_message})


    @database_sync_to_async
    def read_messages(self, chat_id, last_message_id):
        user = self.scope["user"]
        try:
            chat_id = int(chat_id)
            last_message_id = int(last_message_id)
        except Exception as e:
            logger.exception("user state error", exc_info=e)
        if not user.is_staff:
            if not Chat.objects.filter(id=chat_id, user=user).exists():
                return {"error": "Access denied!", "code": 403, "close": True}
        queryset = Message.objects.filter(
            chat__id=chat_id,
            id__lte=last_message_id,
        ).exclude(sender=user)

        if user.is_staff:
            queryset = queryset.exclude(sender__is_staff=True)

        updated_count, _ = queryset.update(read=True)

        return {"type": "rd_msgs", "read_count": updated_count, "last_read_id": last_message_id, "chat_id" : chat_id}


    @database_sync_to_async
    def delete_messages(self, chat_id, deleted_msgs):
        user = self.scope["user"]
        try:
            chat_id = int(chat_id)
            from_id = int(from_id)
            to_id = int(to_id)
        except Exception as e:
            logger.exception("user state error", exc_info=e)
        if not user.is_staff:
            if not Chat.objects.filter(id=chat_id, user=user).exists():
               return {"error": "Access denied!", "code": 403, "close": True}
        queryset = Message.objects.filter(
            chat__id=chat_id,
            id__in=deleted_msgs,
            sender=user
        )

        ids = sorted(queryset.values_list("id", flat=True))
        updated_count, _ = queryset.update(is_delete=True)

        return {"type":"dlt_msgs","deleted_count": updated_count, "deleted_ids": ids, "chat_id": chat_id}

    
    @database_sync_to_async
    def update_message(self, chat_id, msg_id, text_content):
        print("message update ws route")

        user = self.scope["user"]
        try:
            chat_id = int(chat_id)
            msg_id = int(msg_id)
        except Exception as e:
            logger.exception("user state error", exc_info=e)
        if not user.is_staff:
            if not Chat.objects.filter(id=chat_id, user=user).exists():
               return {"error": "Access denied!", "code": 403, "close": True}
        query = Message.objects.get(
            id=msg_id,
            chat__id=chat_id,
            sender=user,
        )

        updated, _ = query.update(text=text_content,updated_at=now())

        

        return {"type":"uptd_msg", "msg": updated, "chat_id": chat_id}


    @database_sync_to_async
    def is_chat_member_or_staff(self, user, chat_id):
        if user.is_staff:
            return True 
        else:
            try:
                chat = Chat.objects.get(id=chat_id)
                return chat.user == user
            except Chat.DoesNotExist:
                return False
        