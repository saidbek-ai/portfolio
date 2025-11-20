-- KEYS[1] = online_staff set
-- KEYS[2] = online_users zset
-- KEYS[3] = private channel prefix (e.g., "user_")
-- ARGV[1] = cutoff timestamp

local online_staff_key = KEYS[1]
local online_users_key = KEYS[2]
local private_channel_prefix = KEYS[3]
local cutoff = tonumber(ARGV[1])

-- Get expired users with scores
local expired = redis.call('ZRANGEBYSCORE', online_users_key, '-inf', cutoff, 'WITHSCORES')
local result = {}

for i = 1, #expired, 2 do
    local user_id = expired[i]
    local score = tonumber(expired[i+1])

    local private_channel_key = private_channel_prefix .. user_id
    local channels = redis.call('SMEMBERS', private_channel_key)

    -- Clean up
    redis.call('ZREM', online_users_key, user_id)
    redis.call('DEL', private_channel_key)

    -- Check staff status
    local is_staff = redis.call('SISMEMBER', online_staff_key, user_id)
    local is_last_staff = 0
    if is_staff == 1 then
        redis.call('SREM', online_staff_key, user_id)
        if redis.call('SCARD', online_staff_key) == 0 then
            is_last_staff = 1
        end
    end

    -- Build entry: {user_id, last_seen, is_staff, is_last_staff, channel1, channel2, ...}
    local entry = {user_id, score, is_staff, is_last_staff}
    for _, ch in ipairs(channels) do
        table.insert(entry, ch)
    end

    table.insert(result, entry)
end

return result

-- [0] The user Id
-- [1] The user last_seen timestamp
-- [2] The is_staff 
-- [3] The is_last_staff 
-- [:4] are the channels

--  Example Output:
--  [
--   [b'42', 1695402450.0, 1, 1, b'chan_abc', b'chan_xyz'],
--    [b'99', 1695402488.0, 0, 0, b'chan_foo']
--  ]