# WebGames
Service de jeux multi-joueur web-friendly

## Requirement
- docker >= 1.11
- docker-compose
- node >= 8.0

## API EndPoints :

| Resource URL | Methods | Description | Requires Token | More information |
| -------- | ------------- | --------- |--------------- | ---------------- |
| `/auth/account`| GET | current user profile | TRUE |
| `/auth/account/reset/` | GET | link receive via e-mail to change password | FALSE | 
| `/auth/account/:id` | GET | specifice user profile | FALSE | public informations |
| `/auth/register` | POST | local register | FALSE | 
| `/auth/login` | POST | local login | FALSE | 
| `/auth/login/admin` | POST | local login admin| FALSE | 
| `/auth/forgot` | POST | give your email and get a url in your email to change password | FALSE |
| `/auth/account/reset` | PUT | change effectively your password | TRUE | 
| `/auth/accound/update` | PUT | update user profile | TRUE |
| `/auth/logout`| DELETE | local logout | TRUE |
| `/auth/unregister`| DELETE | unregister user | TRUE | remove all informations about the user |
| `/queue/states` | GET | get the states about all games | TRUE |
| `/queue/state/:name` | GET | get the state about a specific game | TRUE |
| `/queue/actives` | GET | get all the actives games (only names) | TRUE |
| `/queue/remove` | DELETE | remove a game | TRUE | 
| `/admin` | GET | admin page | TRUE (admin) |
| `/admin/login` | GET | admin login page | FALSE |
| `/admin/update` | PUT | update game | TRUE (admin) |     

## Manager Commands:

| Name | Usage | Description | Usable by |
| ---- | ----- | ----------- | --------- |
| help | `help (?P<command>)?` | Get command list or full help about a specific command. | Clients |
| help | `help command list:( (?P<command>\w+))+` | Give the list of available commands (reply of `help` without command) | Server |
| help | `help (?P<command>\w+) (?P<infos>.*) Usage: (?P<usage>.*)` | Give command informations (reply of `help` with a command) | Server |
| ping | `ping (?P<value>[0-9]{4})` | Send a ping request with a 4 digit random value | Everybody |
| pong | `pong (?P<value>[0-9]{4})` | Reply to a ping, the value must be the same has the one sent in along the ping command. | Everybody |
| quit | `quit (?P<reason>.*)?` | Close the connection, the socket must be closed right after sending or receiving the command. | Everybody |
| error | `error (?P<message>.*)` | informate the client its command failed | Server |
| enable | `enable (?P<game>\w+)` | Enable a game by allowing players to join its queue. | Web API |
| disable | `disable (?P<game>\w+)` | Disable a game by kicking players from its queue and disallow players to join it. | Web API |
| join | `join (?P<queue>\w+)` | Join a game by first joining its queue. | User |
| leave | `leave (?P<queue>\w+)?` | Leave a specific queue if a queue is given or all queues otherwise. | User |


## Installation step

#### Clone the repo
```
git clone git@github.com:EPHEC-TI/WebGames.git
```

#### Create a .env and fill it with the right informations
```
DBURL=postgres://username:password@host:port/database
SECRET=mysecret
```

#### Start all the services at once

```
docker-compose up -d
```

