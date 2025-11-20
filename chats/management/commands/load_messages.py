# yourapp/management/commands/load_messages.py

import json
from pathlib import Path
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive
from django.db import transaction

from chats.models import Message, Chat
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Seed messages from a JSON file"

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            required=True,
            help='Path to the JSON file containing messages'
        )

        parser.add_argument(
            '--chunk-size',
            type=int,
            default=500,
            help='Number of messages to insert in each DB chunk'
        )

    def handle(self, *args, **options):
        file_path = Path(options['file'])
        chunk_size = options['chunk_size']

        if not file_path.exists():
            self.stderr.write(self.style.ERROR(f"❌ File not found: {file_path}"))
            return

        self.stdout.write(f"📥 Loading messages from: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            messages_data = json.load(f)

        chat_ids = {item["chat"] for item in messages_data}
        sender_ids = {item["sender"] for item in messages_data}

        chat_map = {c.id: c for c in Chat.objects.filter(id__in=chat_ids)}
        user_map = {u.id: u for u in User.objects.filter(id__in=sender_ids)}

        message_instances = []

        for item in messages_data:
            chat = chat_map.get(item["chat"])
            sender = user_map.get(item["sender"])
            if not chat or not sender:
                continue

            created_at = parse_datetime(item["created_at"])
            if created_at and is_naive(created_at):
                created_at = make_aware(created_at)

            message = Message(
                chat=chat,
                sender=sender,
                text=item["text"],
                read=item.get("read", False),
                created_at=created_at,
            )
            message_instances.append(message)

        self.stdout.write(f"⚡ Seeding {len(message_instances)} messages...")

        with transaction.atomic():
            for i in range(0, len(message_instances), chunk_size):
                Message.objects.bulk_create(
                    message_instances[i:i+chunk_size],
                    batch_size=chunk_size
                )

        # Optional: Update chat.updated_at
        chat_updates = defaultdict(list)
        for msg in message_instances:
            chat_updates[msg.chat.id].append(msg.created_at)

        for chat_id, times in chat_updates.items():
            Chat.objects.filter(id=chat_id).update(updated_at=max(times))

        self.stdout.write(self.style.SUCCESS("✅ Seeding complete."))
