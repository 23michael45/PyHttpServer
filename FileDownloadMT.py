
# usr/bin/env python                        
# coding: utf-8                        
                    
"""                        
Copyright (c) 2015-2016 cain                        
author: cain <singforcain@gmail.com>                        
"""                        
                        
import time                        
import math                        
import Queue                        
import logging                        
import argparse                        
import requests                        
import threading                        
                        
mutex = threading.Lock()                        
                        
                        
class FileDownload(object):                        
    def __init__(self, url, filename, threadnum, bulk_size, chunk_size):                        
        self.url = url                        
        self.filename = filename                        
        self.threadnum = threadnum                        
        self.bulk_size = bulk_size                        
        self.chunk_size = chunk_size                        
        self.file_size = self.getSize()                        
        self.buildEmptyFile()                        
        self.queue = Queue.Queue(1024)                        
        self.setQueue()                        
                        
                        
    def getSize(self):                        
        """                        
        :return:返回文件的大小，采用head的方式                        
        """                        
        response = requests.head(self.url)                        
        return int(response.headers["content-length"])                        
                        
    def buildEmptyFile(self):                        
        """                        
        建立空文件                        
        :return:                        
        """                        
        try:                        
            logging.info("Building empty file...")                        
            with open(self.filename, "w") as f:                        
                f.seek(self.file_size)                        
                f.write("\x00")                        
                f.close()                        
        except Exception as err:                        
            logging.error("Building empty file error...")                        
            logging.error(err)                        
            exit()                        
                        
    def setQueue(self):                        
        """                        
        根据文件大小以及设置的每个任务的文件大小设置队列                        
        :return:返回队列信息                        
        """                        
        logging.info("Setting the queue...")                        
        tasknums = int(math.ceil(float(self.file_size)/self.bulk_size))  
        # 向上取整
        for i in range(tasknums):                        
            ranges = (self.bulk_size*i, self.bulk_size*(i+1)-1)                        
            self.queue.put(ranges)                        
                        
    def download(self):                        
        while True:                        
            logging.info("Downloading data in %s" % (threading.current_thread().getName()))                        
            if not self.queue.empty():                        
                start, end = self.queue.get()                        
                tmpfile = ""                        
                ranges = "bytes={0}-{1}".format(start, end)                        
                headers = {"Range": ranges}                        
                logging.info(headers)                        
                r = requests.get(self.url, stream=True, headers=headers)                        
                for chunk in r.iter_content(chunk_size=self.chunk_size):                        
                    if not chunk:                        
                        break                        
                    tmpfile += chunk                        
                mutex.acquire()                        
                with open(self.filename, "r+b") as f:                        
                    f.seek(start)                        
                    f.write(tmpfile)                        
                    f.close()                        
                logging.info("Writing [%d]bytes data into the file..." % (len(tmpfile)))                        
                mutex.release()                        
            else:                        
                logging.info("%s is over..." % (threading.current_thread().getName()))                        
                break                        
                        
    def run(self):                        
        threads = list()                        
        for i in range(self.threadnum):                        
            threads.append(threading.Thread(target=self.download))                        
        for thread in threads:                        
            thread.start()                        
        for thread in threads:                        
            thread.join()                        
                        
def logInit():                        
    """                        
    配置日志信息                        
    :return:                        
    """                        
    logging.basicConfig(format='[%(asctime)s]\t[%(levelname)s]\t%(message)s',                        
                        level="DEBUG",                        
                        datefmt="%Y/%m/%d %I:%M:%S %p")                        
                        
                        
def start(url, filename, threadnum):                        
    """                        
    下载部分核心功能                        
    :param url:                        
    :param filename:                        
    :param threadnum:                        
    :return:                        
    """                        
    url = url                        
    filename = filename                        
    threadnum = threadnum if threadnum and threadnum < 20 else 5                        
    bulk_size = 2*1024*1014                        
    chunk_size = 50*1024                        
    print(url, filename, threadnum, bulk_size, chunk_size)                        
    Download = FileDownload(url, filename, threadnum, bulk_size, chunk_size)                        
    Download.run()                        
                        
if __name__ == '__main__':                        
    logInit()                        
    logging.info("App is starting...")                        
    start_time = time.time()                        
    parser = argparse.ArgumentParser()                        
    parser.add_argument("url", help="The file's url")                        
    parser.add_argument("--filename", help="The file's name you want to rename")                        
    parser.add_argument("--threadnum", help="The threads you want to choose", type=int)                        
    args = parser.parse_args()                        
    start(args.url, args.filename, args.threadnum)                        
    logging.info("App in ending...")                        
    logging.info("It consumes [%d] seconds" % (time.time()-start_time))                        

