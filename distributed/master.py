#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import SocketServer
import thread,time
from SimpleXMLRPCServer import SimpleXMLRPCServer

class MultiThreadRPCServer(SocketServer.ThreadingMixIn,SimpleXMLRPCServer):
    pass

global url_set 
global url_pool
global server 
global pool_lock
global set_lock

def add_url(url):
    pool_lock.acquire()
    set_lock.acquire()
    if not(url in url_set) and url.find('html')!=-1 and url.find('ustc')!=-1:
        url_pool.append(url)
    url_set.add(url)
    set_lock.release()
    pool_lock.release()
    return 0

def get_url():
    pool_lock.acquire()
    if len(url_pool)!=0:
        url=url_pool.pop()
    else:
        url=0
    pool_lock.release()
    return url

def stop_parse():
    server.shutdown()
    return 0

if __name__=='__main__':
    initial_url = 'http://staff.ustc.edu.cn/~bjhua/courses/security/2013/index.html'

    url_set = set()
    url_pool = [] 
    #server = MultiThreadRPCServer(("localhost",8000)) 
    server = MultiThreadRPCServer(("192.168.1.100",8000)) 
    pool_lock=thread.allocate_lock()
    set_lock=thread.allocate_lock()

    url_set.add(initial_url)
    url_pool.append(initial_url)

    server.register_function(add_url)
    server.register_function(get_url)
    server.register_function(stop_parse)
    server.serve_forever()

    print url_set




    
