# WebGames
Service de jeux multi-joueur web-friendly

## Requirement
- docker >= 1.11
- docker-compose
- node >= 7.5

## API EndPoints :

| Resource URL | Methods | Description | Requires Token | More information |
| -------- | ------------- | --------- |--------------- | ---------------- |
| `/api/register` | POST | login register | FALSE | 
| `/api/login` | GET | local login | FALSE | 
| `/api/logout`| GET | local logout | TRUE |
| `/api/me`| GET | user profile | TRUE |
| `/api/:u_id` | GET | specifice user profile | FALSE/TRUE | public informations |

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
# api/docker-compose.yml

version: '2'

services:
  db:
    image: postgres
    volumes:
      - ./model/init.sql:/docker-entrypoint-initdb.d/init.sql
    environment:
      - POSTGRES_USER=<user>
      - POSTGRES_PASSWORD=<password>
      - POSTGRES_DB=<db_name>
    ports:
      - 5432:5432
```

```
cd api && docker-compose up -d
```

#### Launch the api server and launch test (why not)
```
yarn server (or npm run server)
yarn test (or npm run test)
```
