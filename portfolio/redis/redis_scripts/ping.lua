-- KEYS[1]: The set of channels for a user, e.g., 'user_channel_123'
-- KEYS[2]: The sorted set of online users, e.g., 'online_users'
-- ARGV[1]: The expiration timeout for the user's channel key
-- ARGV[2]: The user's ID
-- ARGV[3]: The current Unix timestamp

local channels_key = KEYS[1]
local online_users_key = KEYS[2]
local exp_timeout = ARGV[1]
local user_id = ARGV[2]
local current_time = ARGV[3]

-- Update the expiration of the user's connection set.
-- If the set has expired, this command will not create it.
redis.call('EXPIRE', channels_key, exp_timeout)

-- Update the score (last seen time) of the user in the global online users sorted set.
-- If the user doesn't exist, it will be added.
redis.call('ZADD', online_users_key, current_time, user_id)

-- Return a success status to the client
return 1