#!/bin/sh
gunicorn -w 3 -b 0.0.0.0:8000 services.get_status:app &
python3 start.py --type asynq --urls 'http://ya.ru' 'http://mail.ru' 'http://cb-ideas.com' 'http://cb-ideas.ru' 'http://cb-ideas.rut' 'http://google.com' 'http://vk.com'  --interval 2 --concurrency 3 --timeout 1
