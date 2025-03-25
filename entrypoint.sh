#!/bin/bash

# Start MongoDB and gunicorn if not in delivery mode
if [ "$FLASK_ENV" != "delivery" ]; then
    # merge two conditions together
    mongod --dbpath /staycation/data/db &
    gunicorn --bind 0.0.0.0:5000 -m 007 --workers 5 'app:create_app()'
else
    tail -f /dev/null
fi
