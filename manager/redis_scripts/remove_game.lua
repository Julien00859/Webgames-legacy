local game_id = KEYS[1]
local player_cnt = tonumber(KEYS[2])

redis.replicate_commands()
local players_ids = redis.call("SPOP", "games:" .. game_id .. ":players", player_cnt)
for _, player_id in pairs(players_ids) do
    redis.call("DEL", "players:" .. player_id .. ":game")
end
redis.call("DEL", "games:" .. game_id .. ":players")