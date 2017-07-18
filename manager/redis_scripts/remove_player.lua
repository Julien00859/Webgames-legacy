local playerid = KEYS[1]

redis.call("DEL", "players:" .. playerid .. ":queues")
redis.call("DEL", "players:" .. playerid .. ":game")
for idx, queue in pairs(ARGV) do
    redis.call("SREM", "queues:" .. queue, playerid)
end
