#!/usr/bin/env bash
set -e

echo "REDIS_SERVER"
echo "redis local: $REDIS_SERVER_LOCAL"
if [[ "$REDIS_SERVER_LOCAL" = "TRUE" || "$CIRCLE_JOB" = "backend-owasp-scan" ]]; then
    echo "Run redis server on docker"
else
    echo "Run redis server locally"
    export LD_LIBRARY_PATH=/home/vcap/deps/0/lib/:/home/vcap/deps/1/lib:$LD_LIBRARY_PATH
    ( cd  /home/vcap/deps/0/bin/; ./redis-server /home/vcap/app/redis.conf &)
fi

# Collect static files. This is needed for swagger to work in local environment
if [[ $DISABLE_COLLECTSTATIC ]]; then
    echo "DISABLE_COLLECTSTATIC is set to true, skipping collectstatic"
else
    echo "Collecting static files"
    python manage.py collectstatic --noinput
fi

# Celery worker config can be found here: https://docs.celeryq.dev/en/stable/userguide/workers.html#:~:text=The-,hostname,-argument%20can%20expand
celery -A tdpservice.settings worker --loglevel=INFO --concurrency=1 --max-tasks-per-child=1 -n worker1@%h &
sleep 5

# TODO: Uncomment the following line to add flower service when memory limitation is resolved
celery -A tdpservice.settings --broker=$REDIS_URI flower &
celery -A tdpservice.settings beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler &

echo "Starting Gunicorn"
if [[ "$DJANGO_CONFIGURATION" = "Development" || "$DJANGO_CONFIGURATION" = "Local" ]]; then
    gunicorn_params="-c gunicorn_dev_cfg.py"
else
    gunicorn_params="-c gunicorn_prod_cfg.py"
fi

gunicorn_cmd="gunicorn $gunicorn_params"

if [[ $1 == "cloud" ]]; then
    echo "Starting Alloy"
    mkdir /home/vcap/app/alloy-data
    wget https://github.com/grafana/alloy/releases/download/v1.8.1/alloy-boringcrypto-linux-amd64.zip
    unzip -a alloy-boringcrypto-linux-amd64.zip && rm -rf alloy-boringcrypto-linux-amd64.zip
    chmod +x alloy-boringcrypto-linux-amd64
    ./alloy-boringcrypto-linux-amd64 run --server.http.listen-addr=0.0.0.0:12345 --storage.path=/home/vcap/app/alloy-data /home/vcap/app/plg/alloy/alloy.config &

    echo "Starting the Celery Exporter"
    curl -L https://github.com/danihodovic/celery-exporter/releases/download/latest/celery-exporter -o ./celery-exporter
    chmod +x ./celery-exporter
    ./celery-exporter --broker-url=$REDIS_URI --port 9808 &
fi

exec $gunicorn_cmd
