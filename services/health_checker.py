import requests
import threading
import time
import asyncio
import datetime
from db.models import HealthCheckModel
from utils.errors import ParamError


class HealthCheck():

  def __init__(self,**paramsStub):
    self.urls = paramsStub.get("urls", None)
    self.interval = paramsStub.get("interval", 1)
    self.concurrency = paramsStub.get("concurrency", 1)
    self.timeout = paramsStub.get("timeout", 1)

    if self.urls is None:
        raise ParamError

    print("urls list ", len(self.urls), self.urls)

  def run(self):
    while True:
      
      print("Start : %s" % time.ctime())

      self._start_health_check()

      print("End : %s" % time.ctime())
      
      time.sleep(self.interval)

  def _start_health_check(self):
      '''need to be implenmented in childs'''
      pass


class SyncVersion(HealthCheck):

  def _start_health_check(self):
      all_started_at = time.monotonic()
      for url in self.urls:
        started_at = time.monotonic()
        try:
          r = requests.get(url, timeout=self.timeout)
          print(r.url, r.status_code)
          status_code = r.status_code
        except requests.exceptions.ConnectionError:
          print(url, "Url doent exist")  
          status_code = 0
        finally:
          duration = time.monotonic() - started_at
          print("function took" , duration)
          HealthCheckModel.create( url = url, duration = duration, response_code = status_code, date = datetime.datetime.now() )          
      all_total_time = time.monotonic() - all_started_at
      print('====')
      print(f'total time: {all_total_time:.2f} seconds')

class SemaphoreMultithreadVersion(HealthCheck):

  def _start_health_check(self):
    started_at = time.monotonic()
    bs = threading.BoundedSemaphore(self.concurrency)

    threads = [threading.Thread(target=self._ping_and_save, args=(url, bs))
                         for url in self.urls]

    for t in threads:
      t.start()

    for t in threads:
      t.join()    

    total_time = time.monotonic() - started_at
    print('====')
    print(f'total time: {total_time:.2f} seconds')

  
  def _ping_and_save(self,url, bs):
        started_at = time.monotonic()
        bs.acquire()
        try:
          r = requests.get(url, timeout=self.timeout)
          print(r.url, r.status_code)
          status_code = r.status_code
        except requests.exceptions.ConnectionError:
          print(url, "Url doent exist")  
          status_code = 0
        finally:
          duration = time.monotonic() - started_at
          print("function took" , duration)
          HealthCheckModel.create( url = url, duration = duration, response_code = status_code, date = datetime.datetime.now() )
          bs.release()


class AsyncSemaphoreVersion(HealthCheck):
  def _start_health_check(self):
    started_at = time.monotonic()
    asyncio.run(self._main())
    total_time = time.monotonic() - started_at
    print('====')
    print(f'total time: {total_time:.2f} seconds')


  async def _ping_and_save(self,url, bs):
    started_at = time.monotonic()
    await bs.acquire()
    try:
      r = requests.get(url, timeout=self.timeout)
      status_code = r.status_code
      print(r.url, r.status_code)
    except requests.exceptions.ConnectionError:
      print(url, "Url doent exist")  
      status_code = 0
    finally:
      duration = time.monotonic() - started_at
      print("function took" , duration)
      HealthCheckModel.create( url = url, duration = duration, response_code = status_code, date = datetime.datetime.now() )
      bs.release()

  async def _main(self):
    bs = asyncio.Semaphore(value=self.concurrency)
    await asyncio.wait([self._ping_and_save(url, bs) for url in self.urls])
    print("Main Coroutine")

    



class AsyncProducerConsumerVersion(HealthCheck):
  def _start_health_check(self):
    asyncio.run(self._main())
    print("All Workers Completed")

  async def _main(self):
    queue = asyncio.Queue()

    [ queue.put_nowait(url) for url in self.urls ]

    tasks = []
    for i in range(self.concurrency):
        task = asyncio.create_task(self._ping_and_save(queue))
        tasks.append(task)

    # Wait until the queue is fully processed.
    started_at = time.monotonic()
    await queue.join()
    total_time = time.monotonic() - started_at

    # Cancel our worker tasks.
    for task in tasks:
        task.cancel()

    # Wait until all worker tasks are cancelled.
    await asyncio.gather(*tasks, return_exceptions=True)

    print('====')
    print(f'total time: {total_time:.2f} seconds')

  async def _ping_and_save(self, queue):
    while True:
      started_at = time.monotonic()

      url = await queue.get()

      try:
        r = requests.get(url, timeout=self.timeout)
        status_code = r.status_code
        print(r.url, r.status_code)
      except requests.exceptions.ConnectionError:
        print(url, "Url doent exist")  
        status_code = 0
      finally:
        duration = time.monotonic() - started_at
        print("function took" , duration)
        HealthCheckModel.create( url = url, duration = duration, response_code = status_code, date = datetime.datetime.now() )
        queue.task_done()
