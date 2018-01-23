local user_id = KEYS[1]
local server_id = KEYS[2]

redis.call("SET", "players:" .. user_id .. ":server", server_id)