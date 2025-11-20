-- KEYS[1]: private_channel (user's connection set)
-- KEYS[2]: online_users_key (ZSET of all online users)
-- KEYS[3]: staff_online_key (SET of online staff IDs)
-- ARGV[1]: channel_name (this connection)
-- ARGV[2]: user_id
-- ARGV[3]: role ("staff" or "regular")

local private_channel = KEYS[1]
local online_users_key = KEYS[2]
local staff_online_key = KEYS[3]

local channel_name = ARGV[1]
local user_id = ARGV[2]
local role = ARGV[3]

local result = {}

-- Remove the channel from this user's set
redis.call('SREM', private_channel, channel_name)
local remaining_connections = redis.call('SCARD', private_channel)


local is_last_staff = 0
local is_last_connection = 0
if remaining_connections == 0 then
    -- Remove from the global online ZSET
    redis.call('ZREM', online_users_key, user_id)
    is_last_connection = 1

    -- If the user is staff, also remove them from the staff set
    if role == 'staff' then
        redis.call('SREM', staff_online_key, user_id)
        local online_staff_count = redis.call("SCARD", staff_online_key)
        if online_staff_count == 0 then
            -- This was the last staff member online
            is_last_staff = 1
        end
    end
end


result[1] = is_last_connection
result[2] = is_last_staff

return result
