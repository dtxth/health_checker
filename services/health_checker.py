import requests
import threading
import queue
import time
import asyncio
import aiohttp
import datetime
from db.models import HealthCheckModel
from utils.errors import ParamError


class HealthCheck():

  def __init__(self,**params):
    self.urls = params.get("urls", None)
    self.interval = params.get("interval", 1)
    self.concurrency = params.get("concurrency", 1)
    self.timeout = params.get("timeout", 1)

    if self.urls is None:
        raise ParamError

    print("urls list ", len(self.urls), self.urls)

  def run(self):
    '''need to be implenmented in childs'''
    pass


class SyncVersion(HealthCheck):

  def run(self):
    while True:
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
      time.sleep(self.interval)


class SemaphoreMultithreadVersion(HealthCheck):

  def run(self):
    while True:
      urls_queue = self.urls[:]
      started_at = time.monotonic()
      bs = threading.BoundedSemaphore(self.concurrency)
      threads_amount = len(self.urls) if len(self.urls) < self.concurrency else self.concurrency 

      threads = [threading.Thread(target=self._check_health, args=(bs, urls_queue))
                           for _ in range(threads_amount)]

      [ t.start() for t in threads ]
      [ t.join()for t in threads ]

      total_time = time.monotonic() - started_at
      print('====')
      print(f'total time: {total_time:.2f} seconds')
      time.sleep(self.interval)

  
  def _check_health(self,bs, urls_queue):
      while urls_queue:
        url = urls_queue.pop()
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


class ProducerConsumerMultithreadVersion(HealthCheck):

  def run(self):
    while True:
      urls_queue = queue.Queue(len(self.urls))
      [ urls_queue.put_nowait(url) for url in self.urls ]

      started_at = time.monotonic()
      threads_amount = len(self.urls) if len(self.urls) < self.concurrency else self.concurrency 

      threads = [threading.Thread(target=self._check_health, args=(urls_queue,))
                           for _ in range(threads_amount)]

      [ t.start() for t in threads ]
      urls_queue.join()
      [ t.join() for t in threads ]

      total_time = time.monotonic() - started_at
      print('====')
      print(f'total time: {total_time:.2f} seconds')
      time.sleep(self.interval)

  
  def _check_health(self, urls_queue):
      while not urls_queue.empty():
        url = urls_queue.get()
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
          urls_queue.task_done()


class AsyncSemaphoreVersion(HealthCheck):
  def run(self):
    started_at = time.monotonic()
    asyncio.run(self._main())
    total_time = time.monotonic() - started_at
    print('====')
    print(f'total time: {total_time:.2f} seconds')


  async def _check_health(self,url, bs, session):
    started_at = time.monotonic()
    status_code = 0
    await bs.acquire()
    try:
      async with session.get(url, timeout=self.timeout, ssl=False) as r:
        status_code = r.status
        print(r.url, r.status)
    except Exception  as e:
      print(url, e)  
    finally:
      duration = time.monotonic() - started_at
      print("function took" , duration)
      HealthCheckModel.create( url = url, duration = duration, response_code = status_code, date = datetime.datetime.now() )
      bs.release()
      await asyncio.sleep(self.interval)

  async def _main(self):
    async with aiohttp.ClientSession() as session:
      while True:
        bs = asyncio.Semaphore(value=self.concurrency)
        await asyncio.wait([self._check_health(url, bs, session) for url in self.urls])
        print("Main Coroutine")
        await asyncio.sleep(self.interval)
        


class AsyncProducerConsumerVersion(HealthCheck):
  def run(self):
    asyncio.run(self._main())
    print("All Workers Completed")

  async def _main(self):
    async with aiohttp.ClientSession() as session:
      queue = asyncio.Queue()
      while True:

        [ queue.put_nowait(url) for url in self.urls ]

        tasks = []
        for i in range(self.concurrency):
            task = asyncio.create_task(self._check_health(queue, session))
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
        await asyncio.sleep(self.interval)

  async def _check_health(self, queue, session):
    while True:    
        started_at = time.monotonic()
        status_code = 0
        url = await queue.get()

        try:
          async with session.get(url, timeout=self.timeout, ssl=False) as r:
            status_code = r.status
            print(r.url, r.status)
        except Exception as e:
          print(url, e)  
        finally:
          duration = time.monotonic() - started_at
          print("function took" , duration)
          HealthCheckModel.create( url = url, duration = duration, response_code = status_code, date = datetime.datetime.now() )
          queue.task_done()

