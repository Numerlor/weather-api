Run with `docker compose up`.

example .env
```
MYSQL_ROOT_PASSWORD=some_root_pass
MYSQL_PASSWORD=some_not_root_pass
MYSQL_USER=some_user
MYSQL_DATABASE=db
DB_HOST=database
DB_PORT=3306
DB_USER=some_user
DB_PASSWORD=some_not_root_pass
DB_NAME=db
API_URL=http://site:80/weather/
```

Client will simulate requests with a small period, request http://localhost:8000/weather/ for JSON dump of all rows.
