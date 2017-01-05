#-*- coding: gbk -*-

import sys
import re
import signal
import time
import urllib2
import urlparse
from bs4 import BeautifulSoup
from HTMLParser import HTMLParser

import logging
import ConfigParser
import argparse
import Queue

def signal_term_handler():
    SpiderThread.set_terminate_flag(True)

def parse_cmd():
    parser = argparse.ArgumentParser(prog='mini_spider')
    parser.add_argument('--version', '-v', action='version', version='%(prog)s 1.0')
    parser.add_argument('--config', '-c', dest='config', type=str,
            default='conf/spider.conf', help='the configure file')
    args = parser.parse_args()
    return args

def parse_config(args):
    config = ConfigParser.ConfigParser()
    config.read(args.config)

    config_dict['seed_urls_path'] = config.get('spider', 'seed_urls_path')
    config_dict['output_dir'] = config.get('spider', 'output_directory')
    config_dict['max_depth'] = config.getint('spider', 'max_depth')
    config_dict['crawl_interval'] = config.getfloat('spider', 'crawl_interval')
    config_dict['crawl_timeout'] = config.getfloat('spider', 'crawl_timeout')
    config_dict['thread_count'] = config.getint('spider', 'thread_count')
    config_dict['target_url_type'] = config.get('spider', 'target_url')

    return config_dict

def init_url_pool(seed_urls_path):
    url_pool = Queue.Queue()
    depth = 0
    with open(seed_urls_path, 'r') as fd:
        for line in fd:
            seed_url = line.strip()
            url_pool.put([depth, seed_url])
    return url_pool

class WebPageWriter(object):
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def save_page(url, content):
        url = urllib2.quote(url)
        url = url.replace('/', '%2F')
        file_path = '/'.join([self.output_dir, url])
        try:
            with open(file_path, 'wb') as f:
                f.write(content)
                f.flush()
        except IOError as e:
            #logging error


class WebPageParser(HTMLParser):
    def __init__(self, target_url_type):
        HTMLParser.__init__(self)
        self.links = set()
        self.target_url_pattern = re.compile(target_url_type)
        self.target_tags = ['a', 'link', 'img', 'iframe']
        self.target_attributes = ['href', 'src']

    def handle_starttag(self, tag, attrs):   
        if tag in self.target_tags:
            for (variable, value) in attrs:   
                if variable in self.target_attributes and self.target_url_pattern.match(value):   
                    self.links.add(value)   

    def get_links(self):
        result = self.links
        self.links = set()
        return result

class SpiderThread(threading.Thread):
    def __init__(self, url_pool, crawl_interval, crawl_timeout, max_depth, page_parser, page_writer):
        threading.Thread.__init__()
        self.crawl_interval = crawl_interval
        self.crawl_timeout = crawl_timeout
        self.max_depth = max_depth
        self.page_writer = page_writer
        self.page_parser = page_parser

        SpiderThread.url_pool = url_pool
        SpiderThread.done_set = set()
        SpiderThread.done_set_lock = threading.Lock()
        SpiderThread.terminate_flag = False

    def download_page(self, url):
        req = urllib2.Request(url)
        result = ''
        try:
            res_data = urllib2.urlopen(req, timeout = SpiderThread.crawl_timeout)
            result = res_data.read()
            res_data.close()
        except socket.timeout as e:
            #logging timeout error
        return result

    @staticmethod
    def set_terminate_flag(flag):
        SpiderThread.terminate_flag = flag

    def run(self):
        while SpiderThread.terminate_flag != True:
            try:
                depth, url = SpiderThread.url_pool.get()

                #main process
                if url not in SpiderThread.done_set():
                    #download page
                    content = self.download_page(url) 
                    if content != '':
                        #trans encoding to utf8
                        soup = BeautifulSoup(content)
                        content = soup.prettify()
                        #parse page
                        if depth < SpiderThread.max_depth:
                            self.page_parser.feed(content)
                            links = self.page_parser.get_links()
                            for link in links:
                                link = urlparse.urljoin(url, link) 
                                if link not in SpiderThread.done_set:
                                    SpiderThread.url_pool.put([depth + 1, link])

                        #save page
                        self.page_writer.save_page(url, content)

                    SpiderThread.done_set_lock.acquire()
                    SpiderThread.done_set.add(url)
                    SpiderThread.done_set_lock.release()

                SpiderThread.url_pool.task_done()
            except Exception as e:
                #logging error
                SpiderThread.url_pool.task_done()
            except Queue.Empty as e:
                #notice log empty pool
            finally:
                time.sleep(self.crawl_interval)

def main():
    #arg parse & load config path
    args = parse_cmd()

    #config parser
    config_dict = parse_config(args)

    output_dir = config_dict['output_dir'] #done
    seed_urls_path = config_dict['seed_urls_path'] #done
    crawl_timeout = config_dict['crawl_timeout']
    max_crawl_thread_num = config_dict['thread_count'] #done
    max_depth = config_dict['max_depth']
    crawl_interval = config_dict['crawl_interval']
    target_url_type = config_dict['target_url_type'] #done

    #init signal handler
    signal.signal(signal.SIGTERM, signal_term_handler)

    #init page writer
    page_writer = WebPageWriter(target_url_type, output_dir)

    #init page parser
    page_parser = WebPageParser(target_url_type)
    
    #init url pool
    url_pool = init_url_pool(seed_urls_path)

    #worker thread
    worker_list = []
    for index in xrange(max_crawl_thread_num):
        #init thread & start
        spider_thread = SpiderThread(url_pool, crawl_interval, crawl_timeout, max_depth, page_parser, page_writer)
        spider_thread.start()
        worker_list.append(spider_thread)

    #wait url pool to drain
    url_pool.join()
    #set terminate signal to all the thread
    SpiderThread.set_terminate_flag(True)

    for spider_thread in worker_list:
        spider_thread.join()
        
       

    #logger
    logger = logging.getLogger('spider')
    logger.setLevel(logging.DEBUG)
    
    fh = logging.FileHandler('log/spider.log')
    fh.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    
    logger.addHandler(fh)
    
    logger.info('foorbar')

if __name__ == '__main__':
    main()

