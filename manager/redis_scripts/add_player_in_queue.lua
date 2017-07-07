local gamequeue = "queue:" .. KEYS[1]
local playerid = KEYS[2]
local threshold = tonumber(KEYS[3])

redis.call("SADD", gamequeue, playerid)

local playercnt = redis.call("SCARD", gamequeue)
if playercnt == threshold then
	return redis.call("SPOP", gamequeue, threshold)
else
	return nil
end
