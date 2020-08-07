gunicorn -w 3 -b 0.0.0.0:8000 services.get_status:app &
python start.py -as 
