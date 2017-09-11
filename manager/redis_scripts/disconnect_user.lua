local user_id = KEYS[1]

redis.call("DEL", "players:" .. user_id .. ":server")