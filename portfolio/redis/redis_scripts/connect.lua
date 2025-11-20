-- KEYS[1]: The set of channels for a user
-- KEYS[2]: The sorted set of online users
-- KEYS[3]: The set of staff users
-- ARGV[1]: The channel name
-- ARGV[2]: The user ID
-- ARGV[3]: The expiration timeout (seconds)
-- ARGV[4]: The current Unix timestamp
-- ARGV[5]: The maximum allowed connections per user
-- ARGV[6]: The user role ("staff" or "regular")

local channels_key = KEYS[1]
local online_users_key = KEYS[2]
local staff_set_key = KEYS[3]

local channel_name = ARGV[1]
local user_id = ARGV[2]
local current_time = tonumber(ARGV[3])
local MAX_CONNECTIONS = tonumber(ARGV[4])
local user_role = ARGV[5]
local exp_timeout = tonumber(ARGV[6])

local result = {}

-- Add channel to user's set (returns 1 if added, 0 if already present)
local new_connections = redis.call('SADD', channels_key, channel_name)
local current_connection_count = redis.call('SCARD', channels_key)

local is_first_connection = 0
local connection_status = "ok"
local is_first_staff = 0

if new_connections == 1 then
    is_first_connection = 1
end

-- Enforce max connections per user
if current_connection_count > MAX_CONNECTIONS then
    -- Revert addition and mark as exceeded
    redis.call('SREM', channels_key, channel_name)
    connection_status = "limit_exceeded"
else
    -- Valid connection: update expiration and presence
    redis.call('EXPIRE', channels_key, exp_timeout)
    redis.call('ZADD', online_users_key, current_time, user_id)

    if user_role == 'staff' then
        redis.call('SADD', staff_set_key, user_id)
        local staff_set_count = redis.call('SCARD', staff_set_key)
        if staff_set_count == 1 then
            is_first_staff = 1
        end
    end
end

-- Return: status, first_connection_flag, connection_count, first_staff_flag
result[1] = connection_status
result[2] = is_first_connection
result[3] = is_first_staff
result[4] = current_connection_count

return result
