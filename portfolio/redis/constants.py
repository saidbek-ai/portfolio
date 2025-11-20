import os
import time
import logging


def load_lua(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "redis_scripts", filename)

    with open(file_path, "r") as f:
        return f.read()

# ZSet of online user IDs (for all users).
REDIS_ONLINE_USERS_SET = "app:rt:online:users"
# Set of currently online staff IDs (for quick lookup).
REDIS_ONLINE_STAFF_SET = "app:rt:online:staff"
# Hash mapping user_id to a list of active WebSocket channel names for that user.
# REDIS_USER_CONNECTIONS_HASH = "app:rt:connections"

# Channels
# These are Django Channels group names.
# Group for broadcasting presence updates to regular users.
ALL_USERS_PRESENCE_GROUP = "presence"
# Group for broadcasting presence updates to staff.
STAFF_PRESENCE_GROUP = "staff_presence"
STAFF_GROUP = "staff"
# The prefix for a user's private channel. Group name: 'user_<user_id>'.
USER_PRIVATE_GROUP_PREFIX = "user_"

# Configuration
# Timeout for a user's connection. Used to set the key expiration time.
CLEAN_UP_INTERVAL=60 # 60 sec
PRIVATE_CHANNEL_TIMEOUT = int((CLEAN_UP_INTERVAL / 2) * 3) # 90 sec
# Maximum number of concurrent connections allowed per user.
MAX_CONNECTIONS_PER_USER = 4


CONNECT_SCRIPT = load_lua("connect.lua")
DISCONNECT_SCRIPT = load_lua("disconnect.lua")
PING_SCRIPT = load_lua("ping.lua")

CLEAN_UP_SCRIPT = load_lua("clean_up.lua")