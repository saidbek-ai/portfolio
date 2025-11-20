import json
from pathlib import Path
from collections import defaultdict

from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive
from django.db import transaction

from .models import Message, Chat, User


def load_messages_from_json(file_path, chunk_size=500):
    file = Path(file_path)

    if not file.exists():
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"📥 Loading messages from: {file_path}")
    with open(file, "r", encoding="utf-8") as f:
        messages_data = json.load(f)

    # Prefetch Chat and User instances to avoid repeated DB hits
    chat_ids = set(item["chat"] for item in messages_data)
    sender_ids = set(item["sender"] for item in messages_data)

    chat_map = {c.id: c for c in Chat.objects.filter(id__in=chat_ids)}
    user_map = {u.id: u for u in User.objects.filter(id__in=chat_ids)}

    print(f"🔁 Preparing {len(messages_data)} messages for bulk insert...")

    messages_to_insert = []

    for data in messages_data:
        chat = chat_map.get(data["chat"])  
        sender = user_map.get(data["sender"])

        if not chat or not sender:
            continue  # skip if foreign keys are missing

        created_at = parse_datetime(data["created_at"])
        if created_at and is_naive(created_at):
            created_at = make_aware(created_at)

        msg = Message(
            chat=chat,
            sender=sender,
            text=data["text"],
            read=data.get("read", False),
            created_at=created_at
        )
        messages_to_insert.append(msg)

    print(f"⚡ Bulk inserting {len(messages_to_insert)} messages in chunks...")

    with transaction.atomic():
        for i in range(0, len(messages_to_insert), chunk_size):
            Message.objects.bulk_create(
                messages_to_insert[i:i+chunk_size],
                batch_size=chunk_size
            )

    # Optional: update each chat's updated_at to the latest message timestamp
    chat_updates = defaultdict(list)
    for msg in messages_to_insert:
        chat_updates[msg.chat.id].append(msg.created_at)

    for chat_id, timestamps in chat_updates.items():
        Chat.objects.filter(id=chat_id).update(updated_at=max(timestamps))

    print("✅ Done.")

