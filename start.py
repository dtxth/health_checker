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


def main(argv):
   if not argv:
      print("-s sync start")
      print("-m multthread semaphore start")
      print("-as async semaphore start")
      print("-apc async producer consumer start")
      sys.exit(2)
   print(argv)
   # try:
   #    opts, args = getopt.getopt(argv,"s:m:as:apc",["ifile=","ofile="])
   # except getopt.GetoptError:
   #    print ('start.py -s <inputfile> -o <outputfile>')
   #    sys.exit(2)
   # print("=====",opts,args)
   for opt in argv:
      if opt == '-s':
         SyncVersion(**paramsStub).run()
      elif opt == '-m':
         SemaphoreMultithreadVersion(**paramsStub).run()           
      elif opt == '-as':
         AsyncSemaphoreVersion(**paramsStub).run()           
      elif opt == '-apc':
         AsyncProducerConsumerVersion(**paramsStub).run()           

if __name__ == "__main__":
   main(sys.argv[1:])


