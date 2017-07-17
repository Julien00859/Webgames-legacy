local queue = KEYS[1]
local playerid = KEYS[2]
local threshold = tonumber(KEYS[3])
local game_queue = "queues:" .. queue

redis.call("SADD", "players:" .. playerid .. ":queues", queue)
redis.call("SADD", game_queue, playerid)

local playercnt = redis.call("SCARD", game_queue)
if playercnt >= threshold then
	local players = redis.call("SPOP", game_queue, threshold)
	for player in players do
		redis.call("DEL", "players:" .. player .. ":queues")
	end
else
	return nil
end
