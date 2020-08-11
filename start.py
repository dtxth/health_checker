import sys, getopt
from services.health_checker import SyncVersion, SemaphoreMultithreadVersion, \
      AsyncSemaphoreVersion, AsyncProducerConsumerVersion


paramsStub = { "urls" : ['http://ya.ru',
                         'http://mail.ru',
                         'http://cb-ideas.com',
                         'http://cb-ideas.ru',
                         'http://cb-ideas.rut',
                         'http://google.com',
                         'http://vk.com' ],
               "interval": 4,
               "concurrency": 3,
               "timeout": 1
}


#{ "urls" : ['http://ya.ru','http://mail.ru','http://cb-ideas.com','http://cb-ideas.ru','http://cb-ideas.rut','http://google.com','http://vk.com' ],"interval": 4,"concurrency": 3,"timeout": 1}

# python3 start.py --type asynq --urls 'http://ya.ru' 'http://mail.ru' 'http://cb-ideas.com' 'http://cb-ideas.ru' 'http://cb-ideas.rut' 'http://google.com' 'http://vk.com'  --interval 2 --concurrency 3 --timeout 1

import argparse

SCRIPT_CHOICES = ["sync", 'mult', 'asyncsem', 'asynq']

def main(argv):
  if not argv:
      print("--type sync Sync version start")
      print("--type mult Multthread semaphore version start")
      print("--type asyncsem Async semaphore version start")
      print("--type asynq Async producer-consumer version start")
      sys.exit(2)

  CLI = argparse.ArgumentParser()      

  CLI.add_argument(
      "--type",  # name on the CLI - drop the `--` for positional/required parameters
      type=str,
      choices = SCRIPT_CHOICES
    )

  CLI.add_argument(
      "--urls",  # name on the CLI - drop the `--` for positional/required parameters
      nargs="*",  # 0 or more values expected => creates a list
      type=str
    )

  CLI.add_argument(
    "--interval",  # name on the CLI - drop the `--` for positional/required parameters
    type=int,
    default = 4
    ) 
  
  CLI.add_argument(
    "--concurrency",  # name on the CLI - drop the `--` for positional/required parameters
    type=int,
    default = 2
    )   
  CLI.add_argument(
    "--timeout",  # name on the CLI - drop the `--` for positional/required parameters
    type=int,
    default = 1
    ) 
  args = CLI.parse_args(argv)

  params = { "urls" : args.urls,
              "interval": args.interval,
              "concurrency": args.concurrency,
              "timeout": args.timeout}

  print(params)
  if args.type == "sync":
      SyncVersion(**params).run()
  elif args.type == "mult":
      SemaphoreMultithreadVersion(**params).run()           
  elif args.type == "asyncsem":
      AsyncSemaphoreVersion(**params).run()           
  elif args.type == "asynq":
      AsyncProducerConsumerVersion(**params).run()           

if __name__ == "__main__":
   main(sys.argv[1:])


