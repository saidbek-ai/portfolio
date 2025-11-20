from chats.routing import websocket_urlpatterns as chats_ws
from users.routing import websocket_urlpatterns as users_ws

websocket_urlpatterns = [
  *users_ws,
  *chats_ws,
]   