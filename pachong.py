# -*- coding: utf-8 -*-
import os, re, json, traceback
import requests
from bs4 import BeautifulSoup
from pyltp import SentenceSplitter
hrefs = []
meaning = []

class WebScrape(object):
    def __init__(self, word, url):
        self.url = url
        self.word = word

    # 爬取百度百科页面
    def web_parse(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 \
                                             (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'}
        req = requests.get(url=self.url, headers=headers)

        # 解析网页，定位到main-content部分
        if req.status_code == 200:
            soup = BeautifulSoup(req.text.encode(req.encoding), 'lxml')
            return soup
        return None

    # 爬取url
    def get_url(self):
        soup = self.web_parse()
        if soup:
            lis = soup.find('ul', class_="polysemantList-wrapper cmn-clearfix")
            if lis:
                for li in lis('li'):
                    if '<a' in str(li):
                        href = 'https://baike.baidu.com' + li.find('a')['href']
                        hrefs.append(href)
        print(hrefs)

    # 获取该词语的义项
    def get_gloss(self):
        soup = self.web_parse()
        if soup:
            lis = soup.find('ul', class_="polysemantList-wrapper cmn-clearfix")
            if lis:
                for li in lis('li'):
                    if '<a' not in str(li):
                        gloss = li.text.replace('▪', '')
                        meaning.append(gloss)
                        return gloss

        return None

    # 获取该义项的语料，以句子为单位
    def get_content(self):
        # 发送HTTP请求
        result = []
        soup = self.web_parse()
        if soup:
            paras = soup.find('div', class_='main-content').text.split('\n')
            for para in paras:
                if self.word in para:
                    sents = list(SentenceSplitter.split(para))  # 将一段话使用句号分割
                    for sent in sents:
                        if self.word in sent:
                            sent = sent.replace('\xa0', '').replace('\u3000', '')  # 把不同编码下的“空格删除”
                            result.append(sent)

        result = list(set(result))

        return result

    # 将该义项的语料写入到txt
    def write_file(self):
        gloss = self.get_gloss()
        result = self.get_content()
        print(gloss)
        # print(result)
        if result and gloss:
            with open('./%s_%s.txt' % (self.word, gloss), 'w', encoding='utf-8') as f:
                f.writelines([_ + '\n' for _ in result])

    def run1(self):
        self.get_url()
        self.write_file()
        for href in hrefs:
            WebScrape(self.word, href).run2()

    def run2(self):
        self.write_file()



if __name__ == '__main__':
    pass
