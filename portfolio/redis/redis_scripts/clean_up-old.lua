-- KEYS[1] = online_staff set
-- KEYS[2] = online_users zset
-- KEYS[3] = private channel prefix (e.g., "user_")
-- ARGV[1] = cutoff timestamp

local online_staff_key = KEYS[1]
local online_users_key = KEYS[2]
local private_channel_prefix = KEYS[3]
local cutoff = tonumber(ARGV[1])

local expired = redis.call('ZRANGEBYSCORE', online_users_key, '-inf', cutoff, 'WITHSCORES')
local result = {}

for i = 1, #expired, 2 do
    local user_id = expired[i]
    local score = tonumber(expired[i+1])

    local private_channel_key = private_channel_prefix .. user_id
    local channels = redis.call('SMEMBERS', private_channel_key)

    redis.call('ZREM', online_users_key, user_id)
    redis.call('DEL', private_channel_key)

    local is_staff = redis.call('SISMEMBER', online_staff_key, user_id)
    local is_last_staff = 0  -- Default to 0 (false)

    if is_staff == 1 then
        redis.call('SREM', online_staff_key, user_id)
        local remaining = redis.call('SCARD', online_staff_key)
        if remaining == 0 then
            is_last_staff = 1  -- Set to 1 (true)
        end
    end

    local channels_json = '['
    for j, ch in ipairs(channels) do
        channels_json = channels_json .. '"' .. ch .. '"'
        if j < #channels then channels_json = channels_json .. ',' end
    end
    channels_json = channels_json .. ']'

    local obj = string.format(
      '{"user":"%s","last_seen":%d,"is_staff": %d,"is_last_staff":%d, "channels":%s}',
      user_id, score, is_staff, is_last_staff, channels_json
    )
    table.insert(result, obj)
end

return '[' .. table.concat(result, ',') .. ']'

-- Result
-- [
--   {
--     "user": "42",
--     "last_seen": 1695402450,
--     "is_last_staff": 1,
--     "channels": ["chan_abc", "chan_xyz"]
--   }
-- ]