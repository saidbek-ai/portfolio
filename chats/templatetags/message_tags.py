from django import template
from django.utils.timezone import localtime, now
from datetime import timedelta


register = template.Library()

@register.simple_tag
def group_messages(messages, last_read_id=None):
    grouped = []
    current_date = None
    today = now().date()
    yesterday = today - timedelta(days=1)

    new_label_inserted = False

    for msg in messages:
        msg_date = localtime(msg.created_at).date()

        if current_date != msg_date:
            current_date = msg_date

            #humanized date label
            if msg_date == today:
                label = "Today"
            elif msg_date == yesterday:
                label = "Yesterday"
            elif msg_date.year == today.year:
                label = msg_date.strftime("%B %d")  # e.g., June 30
            else:
                label = msg_date.strftime("%B %d, %Y")  # e.g., Dec 25, 2023

            grouped.append({'type': 'date', 'label': label})

        if last_read_id and not new_label_inserted and msg.id > last_read_id:
            
            grouped.append({'type': 'label', 'label': 'New messages'})

            new_label_inserted = True

        grouped.append({'type': 'message', 'data': msg})

    return grouped