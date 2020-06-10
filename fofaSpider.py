#!/usr/bin/env python3
# coding: utf-8

import sys
import re
import time
import xlwt
import base64
import random
import optparse
import requests

from urllib.parse import quote
from lxml import etree

def write_row(sheet,n,row):
    for i in range(0,len(row)):
        sheet.write(n, i, row[i])

def cmdline():
    Usage = 'fofaSpider.py -q "city=\\"Chongqing\\" && protocol==\\"https\\"" _fofapro_ars_session=39b69ecb09351185c37b763063c4a977\n\tcookie非必须,未登录10条，注册用户50条，会员10000条'
    parser = optparse.OptionParser(usage=Usage)
    parser.add_option('-q', '--query', dest='query', help='简单查询语句，高级语法需转义或使用文本方式')
    parser.add_option('-r',dest='source',help='文本文件路径')   # 批量搜索文件
    parser.add_option('-p',dest='startpage',default=1,type=int,help='起始页面')
    (options, args) = parser.parse_args()
    return options,args

class FofaSpider(object):

    def __init__(self,Cookie,query,startpage):
        self.q = quote(query)
        self.qbase64 = quote(str(base64.b64encode(query.encode()),encoding='utf-8'))
        self.UserAgent = ["Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0","Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50","Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2","Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36","Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11","Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16","Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko","Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11","Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36","Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)","Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)","Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50","Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0","Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11","Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)"]
        self.Cookie = Cookie
        self.page = 1
        self.startpage = startpage


    def spider(self):
        name = time.strftime('%Y%m%d_%H%M%S')
        headers = {"User-Agent": random.choice(self.UserAgent), "Cookie": self.Cookie}
        url = 'https://fofa.so/result?q={}&qbase64={}&full=true'.format(self.q, self.qbase64)
        html = requests.get(url=url, headers=headers).text
        pages = re.findall(r'>(\d*)</a> <a class="next_page" rel="next"', html)
        if len(pages) == 0:
            page = 1
        else:
            page = pages[0]
        print("[+] 总共有{}页".format(page))
        print("[+] 查询语句为{}".format(self.q))
        ROW = 1
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet("结果")
        write_row(sheet,0,["URL_or_HOST","Port","Service","Update_time","Area","ASN","Org","Tag","Banner"])
        try:
            pagenum = int(page) + 1
            error_i = 0
            for n in range(self.startpage,pagenum):
                print("[+] 开始查询第{}页".format(n))
                target = 'https://fofa.so/result?page={}&q={}&qbase64={}&full=true'.format(n,self.q, self.qbase64)
                res = requests.get(url=target, headers=headers).text
                selector = etree.HTML(res)
                rows = []
                for list_mod in selector.xpath('//div[@class="list_mod"]'):
                    target = list_mod.xpath('div[@class="list_mod_t"]/a/@href')
                    if not target:
                        target = list_mod.xpath('div[@class="list_mod_t"]/div[@class="ip-no-url"]/text()')
                    if not target:
                        continue
                    port_service = list_mod.xpath('div[@class="list_mod_t"]/div[@class="span"]/span/a/text()')
                    banner = list_mod.xpath('div[@class="list_mod_c"]/div[@class="row"]/div[@class="col-lg-8 list_sx3"]/div[@class="auto-wrap"]/text()')
                    update_time = list_mod.xpath('string(div[@class="list_mod_c"]/div[@class="row"]/div[@class="col-lg-4"]/ul[@class="list_sx1"]/li/i[@class="fa fa-clock-o"]/..)').strip().replace("\n","").replace("  ","")
                    area = list_mod.xpath('string(div[@class="list_mod_c"]/div[@class="row"]/div[@class="col-lg-4"]/ul[@class="list_sx1"]/li/i[@class="fa fa-plane"]/..)').strip().replace("\n","").replace("  ","")
                    asn = list_mod.xpath('string(div[@class="list_mod_c"]/div[@class="row"]/div[@class="col-lg-4"]/ul[@class="list_sx1"]/li/i[@class="fa fa-plane"]/../following-sibling::*[1])').strip().replace("\n","").replace("  ","")
                    org = list_mod.xpath('string(div[@class="list_mod_c"]/div[@class="row"]/div[@class="col-lg-4"]/ul[@class="list_sx1"]/li/i[@class="fa fa-plane"]/../following-sibling::*[2])').strip().replace("\n","").replace("  ","")
                    tag = list_mod.xpath('string(div[@class="list_mod_c"]/div[@class="row"]/div[@class="col-lg-4"]/ul[@class="list_sx1"]/li/span[@class="list_xs2"]/..)').strip().replace("\n","").replace("  ","")

                    row = []
                    row.append(target[0].strip())
                    port = service = ""
                    for i in port_service:
                        i = i.strip()
                        if i.isdigit():
                            port = i
                        else:
                            service = i
                    row.append(port)
                    row.append(service)
                    row.append(update_time)
                    row.append(area)
                    row.append(asn)
                    row.append(org)
                    row.append(tag)
                    row.append("\n".join(banner).strip())
                    write_row(sheet,ROW,row)
                    ROW += 1
                    rows.append(row)
                    print("[+] {}".format(target[0].strip()))
                print("[+] 第{}页获取到{}条数据".format(n,len(rows)))
                # 等待5-8秒
                time.sleep(random.randint(5,8))
                if not rows:
                    error_i += 1
                if error_i > 4:
                    print("[-] 连续5次未获取到数据，即将结束本次查询")
                    break
        except KeyboardInterrupt:
            print("[-] Ctrl+C ，手动结束本次查询")
        except Exception as e:
            print("[!]爬虫异常退出！")
            print(e)
        if ROW > 1:
            workbook.save('./{}.xls'.format(name))
            print('[+] 搜集结果为{}.xls\n\n'.format(name))
        else:
            print("[-] 搜索无结果")

    def run(self):
        self.spider()

if __name__ == '__main__':
    options, args = cmdline()
    cookie = "".join(args)
    if not options.source and not options.query:
        sys.exit("[-] try:  {} -h".format(sys.argv[0]))
    if options.source:
        with open(options.source,'r+',encoding='utf-8') as file:
            for value in file.readlines():
                value = value.strip('\n')
                spider = FofaSpider(cookie, value, options.startpage)
                spider.run()
    else:
        spider = FofaSpider(cookie,options.query, options.startpage)
        spider.run()

