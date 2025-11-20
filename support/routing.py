from django.urls import re_path
from . import consumer

websocket_urlpatters = [
  re_path(r'ws/support/(?P<ticket_token>[0-9a-f-]+)/$', consumer.AnonymousTicketConsumer.as_asgi()),
]
