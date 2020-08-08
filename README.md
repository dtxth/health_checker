# health_checker

## This is a test task for checking availability of different urls

To start do:

> docker-compose up


To start check use script start.py with keys:
>  -s sync start 

>  -m multthread semaphore start

>  -as async semaphore start 

>  -apc async producer consumer start

To get all checking states use next GET request:
> http://0.0.0.0:8000/states  
