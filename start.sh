#!/bin/bash
python manage.py migrate
uwsgi --http :8080 --module allez.wsgi:application
