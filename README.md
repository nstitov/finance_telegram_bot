# Finance Bot

<a href="https://hub.docker.com/r/nstitov/finance_tg_bot"><img src="https://img.shields.io/badge/Docker%20Hub-blue"></a> 
<a href="https://t.me/TitovNS_FinanceBot"><img src="https://img.shields.io/badge/Telegram-%20@TitovNS_FinanceBot-black"></a>  

This is Telegram bot to manage your finance.

## Used technology
* Python 3.11;
* aiogram 3.x (Telegram Bot framework);
* Docker and Docker Compose (containerization);
* PostgreSQL (database);
* Redis (persistent storage for some ongoing game data);
* SQLAlchemy (working with database from Python);
* Docker images are built with buildx for both amd64 and arm64 architectures.

## Installation

Create a directory of your choice, let's say `/opt/finance_bot`. Inside it, make 4 directories for bot's data:  
`mkdir -p {pg/init,pg/data,redis/config,redis/data}`

Grab `docker-compose.yml` file and put it to `/opt/finance_bot`.

Grab `redis.conf.example` file, rename it to `redis.conf` and put into `/opt/finance_bot/redis/config` directory. 
Change its values for your preference.

Grab `pg_init_user.sh.eample` file, rename it to `pg_init_user.sh`, put it into `/opt/finance_bot/pg/init` and
make executable (add "x" flag). Open it, replace `user_db` values with your own. Save file.

Grab `.env.example` file, rename it to `.env` and put it next to your `docker-compose.yml`, open 
and fill the necessary data. Pay attention to POSTGRES_DSN value, sync it with `pg_init_user.sh` file values.

Finally, start your bot with `docker-compose up -d` command.
