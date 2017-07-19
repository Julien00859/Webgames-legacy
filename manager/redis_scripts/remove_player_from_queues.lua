for idx, pid in pairs(KEYS) do
    redis.call("DEL", "players:" .. pid .. ":queues")
    for idxx, queue in pairs(ARGV) do
        redis.call("SREM", "queues:" .. queue, pid)
    end
end
