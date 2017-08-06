# encoding: utf-8

import os
import time
import urllib

import requests

from lxml import html


def download_img(url, img_name):
    try:
        urllib.urlretrieve(url, img_name)
    except IOError:
        print url


start_time = time.time()

JIANDAN_URL = 'http://jiandan.net/ooxx'
PAGE_URL = 'http://jiandan.net/ooxx/page-{number}#comments'

headers = {
    # 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    # 'accept-encoding': 'gzip, deflate',
    # 'accept-language': 'zh-cn,zh;q=0.8',
    # 'connection': 'keep-alive',
    # 'host': 'jiandan.net',
    # 'upgrade-insecure-requests': '1',
    'user-agent': 'mozilla/5.0 (macintosh; intel mac os x 10_12_5) applewebkit/537.36 (khtml, like gecko) chrome/59.0.3071.115 safari/537.36'
}

req = requests.session()
req.headers.update(headers)
res = req.get(JIANDAN_URL)

home_page = html.fromstring(res.text)


SUCCEED_SIGN = u'妹子图'

title = home_page.xpath('//div[@id="content"]/h1')[0]
if title == SUCCEED_SIGN:
    print 'Login jiandan succeed'
else:
    print 'Login jiandan succeed'

total_page = int(home_page.xpath('//span[@class="current-comment-page"]')[0].text[1:-1])

# total_page = 40
pages = range(1, total_page + 1)
pages.reverse()

count = 0
begin = time.time()
for number in pages:
    try:
        res = req.get(PAGE_URL.format(number=number))
    except:
        continue
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
            try:
                url = li[i].xpath('.//p[1]/a[1]')[0].get('href')
            except:
                continue
            if 'http:' not in url:
                url = 'http:' + url
        image_name = 'temp/{0}-{1}-'.format(number, count) + li[i].xpath('.//span[@class="righttext"]/a')[-1].text + '.' + split_url[-1]
        count += 1
        if not os.path.isfile(image_name):
            # print 'downloading {0} page No.{1} {2}'.format(number, count, image_name)
            download_img(url, image_name)
            # try:
            #     download_img(url, image_name)
            # except IOError:
            #     print 'Error downloading {0} page No.{1} {2}'.format(number, count, url)
            #     continue
print 'All down in ', time.time() - begin
