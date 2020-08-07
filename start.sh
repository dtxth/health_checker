#!/bin/sh
gunicorn -w 3 -b 0.0.0.0:8000 services.get_status:app &
python3 start.py -as 
