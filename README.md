# health_checker

## This is a test task for checking availability of different urls

To start do:

> docker-compose up


To start check use script start.py with keys:
```
--type sync Sync version start
--type mult Multthread semaphore version start
--type pc Multthread Producer Consumer version start
--type asyncsem Async semaphore version start
--type asynq Async producer-consumer version start

example: python3 start.py --type asynq --urls 'http://ya.ru' 'http://mail.ru' 'http://cb-ideas.com' 'http://cb-ideas.ru' 'http://cb-ideas.rut' 'http://google.com' 'http://vk.com'  --interval 2 --concurrency 3 --timeout 1
```

To get all checking states use next GET request:
> http://0.0.0.0:8000/states  
