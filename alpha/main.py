#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2

initial_url = 'http://staff.ustc.edu.cn/~bjhua/courses/security/2013/index.html'

#url_pool = set()
url_pool = [] 

#print dir(url_pool)
#url_pool.add(initial_url)
url_pool.append(initial_url)
print dir(list)

#print url_pool
for url in url_pool:
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
            #print url
            if url.find('http')<0 and url.find('https')<0:
                url =  'http://staff.ustc.edu.cn/~bjhua/courses/security/2013/'+url
            #url_pool.add(url)
            if url_pool.count(url) == 0 and url.find('html')!=-1 and url.find('ustc')!=-1:
                url_pool.append(url)
            result = result[result.find('href')+1:]
    except urllib2.URLError,e:
        if hasattr(e, 'reason'):
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
        elif hasattr(e, 'code'):
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
    #    else:
print url_pool


    
