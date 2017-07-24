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
| `/queue/` | GET | get the whole queue | TRUE (admin) | queue is all the games available on Webgames |
| `/queue/actives` | GET | get all the actives games (only names) | TRUE (admin) |
| `/admin/:name` | GET | get all the informations about a game | TRUE (admin) | 
| `/admin/:name/:attr` | GET | get attribute of a game (e.g.: max players) | TRUE (admin) | 
| `/queue/:name` | POST | add game | TRUE (admin) | 
| `/queue/:name` | PUT | update game | TRUE (admin) |  
| `/queue/:name` | DELETE | delete game | TRUE (admin) | 
| `/admin` | GET | admin page | TRUE (admin) |
| `/admin/login` | GET | admin login page | FALSE |
   

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

#### Install the dependencies
```
yarn (or npm install)
```

#### Init the developpment database
```yml
# docker-compose.yml

version: '2'

services:
  db:
    image: postgres
    environment:
      - POSTGRES_USER=<user>
      - POSTGRES_PASSWORD=<password>
      - POSTGRES_DB=<db_name>
    ports:
      - 5432:5432
```

```
docker-compose up -d
```

#### Launch the api server 
```
yarn server (or npm run server)
```
