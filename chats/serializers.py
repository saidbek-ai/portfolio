from rest_framework import serializers
# from django.contrib.auth.models import User, CustomUser
from django.contrib.auth import get_user_model
from .models import Message, Chat

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'image', 'first_name', 'last_name', 'last_seen',]



class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['file', 'text', 'id', 'chat', 'sender', 'read', 'read_by', 'created_at', 'updated_at', 'deleted_at', 'idempotency_key' ]
        read_only_fields = ['id', 'chat', 'sender', 'read', 'read_by', 'created_at', 'updated_at', 'deleted_at']


class ChatSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_messages = serializers.SerializerMethodField()
    # messages = MessageSerializer(many=True, read_only=True)

    def get_last_message(self, obj):
        user = self.context["request"].user

        if user.is_staff:
            last_msg = obj.messages.last()
            return MessageSerializer(last_msg).data if last_msg else None
        return None
    
    def get_unread_messages(self, obj):
        user = self.context["request"].user

        print(obj)

        if user.is_staff:
            return obj.messages.filter(read=False, deleted_at__isnull=True, sender__is_staff=False).count()

        return obj.messages.filter(read=False).exclude(sender=user).count()

    class Meta:
        model = Chat
        fields = ['id', 'user', 'updated_at', 'last_message', 'unread_messages']