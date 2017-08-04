local player_id = KEYS[1]

local queue_cnt = redis.call("SCARD", "players:" .. player_id .. ":queues")
local queues = redis.call("SPOP", "players:" .. player_id .. ":queues", queue_cnt)
for _, queue in pairs(queues) do
    redis.call("SREM", "queues:" .. queue, player_id)
end
