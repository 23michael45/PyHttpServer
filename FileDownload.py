# usr/bin/env python
# coding: utf-8
"""
Copyright (c) 2015-2016 cain
author: cain <singforcain@gmail.com>
"""
import os
import time
import logging
import datetime
import requests
import argparse
class fileDownload(object):
    def __init__(self, url, file_name):
        """
        :param url:文件的下载地址
        :param file_name:重命名文件的名字
        :return:
        """
        self.url = url
        self.file_name = file_name
        self.stat_time = time.time()
        self.file_size = self.getSize()
        self.offset = self.getOffset()
        self.downloaded_size = self.offset
        self.headers = self.setHeaders()
        self.tmpfile = bytearray()
        self.info()
    def info(self):
        logging.info("Downloaded    [%s] bytes" % (self.offset))
    def setHeaders(self):
        """
        根据已下载文件的大小设置Range头部范围并返回
        :return:
        """
        start = self.offset
        end = self.file_size - 1
        range = "bytes={0}-{1}".format(start, end)
        return {"Range": range}
    def getOffset(self):
        if os.path.exists(self.file_name):
            if self.file_size == os.path.getsize(self.file_name):
                exit()
            else:
                return os.path.getsize(self.file_name)
        else:
            return 0
    def getSize(self):
        """
        :return:返回文件的大小，采用head的方式
        """
        response = requests.head(self.url)
        return int(response.headers["content-length"])
    def download(self):
        """
        断点续传的核心部分
        :return:
      
        """
        with open(self.file_name, "ab") as f:
            try:
                r = requests.get(self.url, stream=True, headers=self.headers)
                for chunk in r.iter_content(chunk_size=1024):
                    if not chunk:
                        break
                    self.tmpfile += (chunk)
                    if len(self.tmpfile) == 1024*50:
                        f.write(self.tmpfile)
                        self.downloaded_size += len(self.tmpfile)
                        logging.info("Downloaded ---[%.2f%%] [%s/%s] bytes" % (float(self.downloaded_size)/self.file_size*100, self.downloaded_size, self.file_size))
                        self.tmpfile =  bytearray()
            except KeyboardInterrupt:
                logging.warning("Interruped by user")
                logging.info("Ending the thread,please do not exit")
            finally:
                f.write(self.tmpfile)
                self.downloaded_size += len(self.tmpfile)

                logging.info("Downloaded ---[%.2f%%] %s/%s bytes" % (float(self.downloaded_size)/self.file_size*100,self.downloaded_size, self.file_size))
                consume = int(time.time()) - self.stat_time
                logging.info("It consumes %d seconds" % (consume))

                t = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
                s = "End at {}".format(t);
                logging.info(str(s.encode('utf-8').strip() + b"\n"))
            
def init():
    """
    配置日志信息
    :return:
    """
    logging.basicConfig(format='[%(asctime)s]\t[%(levelname)s]\t%(message)s',
                    level="DEBUG",
                    datefmt="%Y/%m/%d %I:%M:%S %p"
                    )
def run(url, name):
    if not name:
        name = url.split("/")[-1]
    file = fileDownload(url, name)
    file.download()
if __name__ == '__main__':
    init()
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="The file's url")
    parser.add_argument("--name", help="The file's name you want to rename")
    args = parser.parse_args()
    run(args.url, args.name)
