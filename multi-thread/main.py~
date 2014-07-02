#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import threading,time


def parse_page():
    wait=0
    while True:
        if len(url_pool)==0:
            time.sleep(1)
            wait=wait+1
            if wait>1:
                break
        else:
            wait=0
            pool_lock.acquire()
            url=url_pool.pop()
            pool_lock.release()

            print url

            req = urllib2.Request(url)
            try:
                res_data = urllib2.urlopen(req)
                result = res_data.read()
                res_data.close()
                while result.find('href') >= 0:
                    url = result[result.find('href'):]
                    url = url[url.find('\"')+1:]
                    url = url[:url.find('\"')]
                    if url.find('http')<0 and url.find('https')<0:
                        url =  'http://staff.ustc.edu.cn/~bjhua/courses/security/2013/'+url
                    #url_pool.add(url)
                    pool_lock.acquire()
                    set_lock.acquire()
                    if not(url in url_set) and url.find('html')!=-1 and url.find('ustc')!=-1:
                        url_pool.append(url)
                        url_set.add(url)
                    set_lock.release()
                    pool_lock.release()
                    result = result[result.find('href')+1:]
            except urllib2.URLError,e:
                if hasattr(e, 'reason'):
                    print 'We failed to reach a server.'
                    print 'Reason: ', e.reason
                elif hasattr(e, 'code'):
                    print 'The server couldn\'t fulfill the request.'
                    print 'Error code: ', e.code
    #    else:

if __name__=='__main__':
    initial_url = 'http://staff.ustc.edu.cn/~bjhua/courses/security/2013/index.html'

    url_set = set()
    url_pool = [] 

    url_set.add(initial_url)
    url_pool.append(initial_url)

    pool_lock=threading.Lock()
    set_lock=threading.Lock()
    #parse_page()

    thread_list=[]
    for i in range(4):
        t=threading.Thread(target=parse_page)
        t.start()
        thread_list.append(t)
    for t in thread_list:
        t.join()
    print url_set




    
