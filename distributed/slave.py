#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import time
from xmlrpclib import ServerProxy


def parse_page(server):
    wait=0
    while True:
        print 'hahaha'
        url=server.get_url()
        if url==0:
            time.sleep(1)
            wait=wait+1
            if wait>3:
                server.stop_parse()
                break
        else:
            wait=0

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
                    server.add_url(url)
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
    #server=ServerProxy("http://localhost:8000")
    server=ServerProxy("http://192.168.1.100:8000")
    parse_page(server)
