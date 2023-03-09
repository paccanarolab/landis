#!/bin/bash

# if [ "$DATABASE" == "postgres" ];
# then
#     echo "Waiting for PostgreSQL initialization..."
# 
#     while ! nc -z $SQL_HOST $SQL_PORT; do
#         sleep 0.1
#     done
# 
#     echo "PostgreSQL started"
# fi

exec "$@"
