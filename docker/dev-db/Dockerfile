FROM mariadb:10.1

ENV MYSQL_ROOT_PASSWORD wikipedia
COPY enwp10_dev.sample.sql /docker-entrypoint-initdb.d
