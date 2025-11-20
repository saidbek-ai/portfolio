from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Chat(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="chats", unique=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def last_message(self):
        return self.messages.order_by("-created_at").first()

    def unread_messages(self, for_user):
        return self.messages.filter(read=False).exclude(sender=for_user).count()

    def __str__(self):
        return f"Chat of {self.user.first_name}"


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    text = models.TextField()
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    read = models.BooleanField(default=False)
    read_by = models.ManyToManyField(User, blank=True, related_name="read_messages")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    # is_deleted = models.BooleanField(default=False)
    idempotency_key = models.CharField(max_length=64, unique=True, db_index=True, null=True, blank=True)

    # created_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.chat.updated_at = self.created_at
        self.chat.save(update_fields=['updated_at'])
    
    class Meta:
        indexes = [models.Index(fields=['chat', 'created_at'])]

    def __str__(self):
        return f"{self.sender.first_name}: {self.text}"
