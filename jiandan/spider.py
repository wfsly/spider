# encoding: utf-8

import os
import threading
import urllib

from multiprocessing import Pool, Process
from threading import Thread

import requests
from lxml import html

import settings


def show_time(func):
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        print 'Cost: {}'.format(end - start)
    return wrapper


class JianDan(object):
    PROJECT_NAME = 'jiandan'
    IMAGE_DIR = os.path.join(settings.IMAGE_DIR, PROJECT_NAME + '/')
    HOME_PAGE_URL = 'http://jiandan.net/ooxx/'
    CONTENT_PAGE_URL_TEMPLATE = HOME_PAGE_URL + 'page-{number}#comments'
    HEADERS = {
        'user-agent': 'mozilla/5.0 (macintosh; intel mac os x 10_12_5) applewebkit/537.36 (khtml, like gecko) chrome/59.0.3071.115 safari/537.36'
    }
    PAGE_NUMBER_XPATH = '//span[@class="current-comment-page"]'
    SUCCEED_SIGN = u'妹子图'
    count = 0

    def __init__(self):
        self._check_images_dir()
        self.req = requests.session()
        self.req.headers.update(self.HEADERS)
        self._request_home_page()
        self._get_total_page_number()

    def _request_home_page(self):
        res = self.req.get(self.HOME_PAGE_URL)
        self.home_page = html.fromstring(res.text)
        title = self.home_page.xpath('//div[@id="content"]/h1')[0]
        if title == self.SUCCEED_SIGN:
            print 'Login jiandan succeed'
        else:
            print 'Login jiandan succeed'

    def _check_images_dir(self):
        if not os.path.exists(self.IMAGE_DIR):
            os.makedirs(self.IMAGE_DIR)

    def _get_total_page_number(self):
        self.total_page_number = int(self.home_page.xpath(self.PAGE_NUMBER_XPATH)[0].text[1:-1])
        print '妹子图共{0}页'.format(self.total_page_number)
        self.pages = range(1, self.total_page_number + 1)
        self.pages.reverse()
        self.each_process = self.total_page_number / int(settings.PROCESS_NUMBER) + 1

    def download_img(self, url, img_name):
        try:
            urllib.urlretrieve(url, img_name)
        except IOError:
            print url
            pass

    def parse_imge(self, process, page_number):
        try:
            res = self.req.get(self.CONTENT_PAGE_URL_TEMPLATE.format(number=page_number))
        except:
            return
        page = html.fromstring(res.text)
        count = 0

        li = page.xpath('//ol[@class="commentlist"]/li')
        total = len(li)

        for i in range(0, total):
            try:
                url = 'http:' + li[i].xpath('.//p[1]/img')[0].get('src')
            except IndexError:
                p = li[i].xpath('.//p[@class="bad_content"]')
                if len(p):
                    continue
            split_url = url.split('.')
            if split_url[-1] == 'gif':
                try:
                    url = li[i].xpath('.//p[1]/a[1]')[0].get('href')
                except:
                    continue
                if 'http:' not in url:
                    url = 'http:' + url
            image_name = self.IMAGE_DIR + 'process-{0}-{1}-{2}-'.format(process, page_number, count) + li[i].xpath('.//span[@class="righttext"]/a')[-1].text + '.' + split_url[-1]
            count += 1
            if not os.path.isfile(image_name):
                # print 'Process {0} downloading {1} page No.{2} {3}'.format(process, page_number, count, image_name[-21:])
                # sys.stdout.flush()
                self.download_img(url, image_name)
                # try:
                #     download_img(url, image_name)
                # except IOError:
                #     print 'Error downloading {0} page No.{1} {2}'.format(number, count, url)
                #     continue

    @show_time
    def start(self, process, start_page, end_page):
        begin = time.time()
        for number in range(start_page, end_page):
            self.parse_imge(process, number)
        print 'Process-{} Done'.format(process), time.time() - begin

    def multiprocess_run(self):
        """
        多进程入口
        """
        self.process = []
        process_number = 0
        total_page_number = self.total_page_number
        each_process = self.each_process
        for i in range(1, total_page_number + 1, each_process):
            process_number += 1
            p = Process(target=self.start, args=(process_number, i, i + each_process, ))
            print p.pid, p.name, ' start'
            p.start()
            time.sleep(3)
            self.process.append(p)
        for i in self.process:
            i.join()


    def multithread_run(self):
        """
        多线程入口
        """
        thread_number = 0
        total_page_number = self.total_page_number
        each_process = self.each_process
        for i in range(1, total_page_number + 1, each_process):
            thread_number += 1
            p = Thread(target=self.start, args=(thread_number, i, i + each_process, ))
            p.start()
            print '{} start'.format(thread_number)
            time.sleep(3)

        main_thread = threading.currentThread()
        for t in threading.enumerate():
            if t is main_thread:
                continue
            t.join()

    def run(self):
        for number in self.pages:
            res = self.req.get(self.CONTENT_PAGE_URL_TEMPLATE.format(number=number))
            page = html.fromstring(res.text)

            li = page.xpath('//ol[@class="commentlist"]/li')
            total = len(li)

            for i in range(0, total):
                try:
                    url = 'http:' + li[i].xpath('.//p[1]/img')[0].get('src')
                except IndexError:
                    p = li[i].xpath('.//p[@class="bad_content"]')
                    if len(p):
                        continue
                split_url = url.split('.')
                if split_url[-1] == 'gif':
                    url = 'http:' + li[i].xpath('.//p[1]/a[1]')[0].get('href')
                image_name = 'images/' + li[i].xpath('.//span[@class="righttext"]/a')[-1].text + '.' + split_url[-1]
                self.count += 1
                if not os.path.isfile(image_name):
                    # print 'downloading {0} page No.{1} {2}'.format(number, self.count, image_name)
                    self.download_img(url, image_name)
                    # try:
                    #     download_img(url, image_name)
                    # except IOError:
                    #     print 'Error downloading {0} page No.{1} {2}'.format(number, count, url)
                    #     continue


if __name__ == "__main__":
    import time
    from datetime import datetime
    begin = time.time()
    print 'start at: ', datetime.fromtimestamp(time.time())
    # JianDan().multiprocess_run()
    JianDan().multithread_run()
    print 'All down in ', time.time() - begin
