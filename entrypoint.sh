#!/bin/sh
python manage.py migrate
python ./manage.py loaddata data/polls-v4.json data/votes-v4.json data/users.json
python manage.py runserver 0.0.0.0:8000