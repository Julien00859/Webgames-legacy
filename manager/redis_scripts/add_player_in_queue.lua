local queue = KEYS[1]
local playerid = KEYS[2]
local threshold = tonumber(KEYS[3])
-- list of all queues in ARGV

redis.replicate_commands()
redis.call("SADD", "players:" .. playerid .. ":queues", queue)
redis.call("SADD", "queues:" .. queue, playerid)

local playercnt = redis.call("SCARD", "queues:" .. queue)
if playercnt >= threshold then
	local players = redis.call("SPOP", "queues:" .. queue, threshold)
	for _, id in pairs(players) do
		redis.call("DEL", "players:" .. id .. ":queues")
		redis.call("SET", "players:" .. id .. ":game", queue)
	end
	for _, game in pairs(ARGV) do
		for _, id in pairs(players) do
			redis.call("SREM", "queues:" .. game, id)
		end
	end
	return players
else
	return nil
end
