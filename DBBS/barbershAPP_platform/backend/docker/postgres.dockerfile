FROM postgis/postgis:14-3.3

COPY ./scripts/init-db.sql /docker-entrypoint-initdb.d/