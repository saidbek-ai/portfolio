import uuid
from django.db import models


class AnonymousTicket(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket {self.token} ({'Resolved' if self.is_resolved else 'Open'})"

class TicketMessage(models.Model):
    ticket = models.ForeignKey(AnonymousTicket, on_delete=models.CASCADE, related_name="messages")
    sender_type =models.CharField(
        max_length=10,
        choices=[("user", "User"), ("agent", "Agent")]
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]
      
    def __str__(self):
        return f"{self.sender_type.upper()} message in {self.ticket.token}"