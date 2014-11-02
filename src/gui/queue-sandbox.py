# coding: utf-8

from Queue import Queue
from threading import Thread
fifo = Queue()
def worker(q):
    while True:
        d = q.get()
        print d
        q.task_done()

wt = Thread(target=worker, name="worker thread", args=(fifo,))
wt.setDaemon(True)
wt.start()

fifo.put("Foobar")

