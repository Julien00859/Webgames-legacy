local queues = KEYS[1]
local playerid = KEYS[2]

redis.call("DEL", "players:" .. playerid .. ":queues")
for queue in queues.split(",") do
    redis.call("SREM", "queues:" .. queue, playerid)
end
