#-*- coding:utf-8 -*-
__author__ = 'Danny'
#get the former 5 pages data
#matplotlib设置中文
#plt.rcParams['font.sans-serif'] = ['SimHei']
#plt.rcParams['axes.unicode_minus'] = False

import re
from http import cookiejar
from urllib import request
from lxml import etree as e
import json
import matplotlib.pyplot as plt


#url = 'https://list.jd.com/list.html?cat=9987,653,655&page=2&sort=sort_totalsales15_desc&trans=1&JL=6_0_0'
url = 'https://list.jd.com/list.html?cat=9987,653,655&page=1&sort=sort%5Ftotalsales15%5Fdesc&trans=1&JL=4_2_0'
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
}

data_list = []
data_num = []

cookie = cookiejar.MozillaCookieJar()
handler = request.HTTPCookieProcessor(cookie)
opener = request.build_opener(handler)
req = request.Request(url, headers=headers)
res = opener.open(req).read().decode()
cookie.save('cookie.txt',ignore_expires=True,ignore_discard=True)
cookie.load('cookie.txt',ignore_expires=True,ignore_discard=True)
cookie = cookiejar.MozillaCookieJar()
handler = request.HTTPCookieProcessor(cookie)
opener = request.build_opener(handler)

#按销量

def gethtml(number):
    for num in range(1,number+1):
        url = 'https://list.jd.com/list.html?cat=9987,653,655&page=' + str(num) + '&sort=sort%5Ftotalsales15%5Fdesc&trans=1&JL=4_2_0'
        req = request.Request(url, headers=headers)
        res = opener.open(req).read().decode()
        num_lenpath = r'li class="gl-item"'
        num_lenpathing = re.compile(num_lenpath)
        length = len(num_lenpathing.findall(res,re.S))+1
        for num in range(1,length):
            #path = '//*[@id="plist"]/ul/li[%d]/div/div[4]/a/@href' % (num)
            path2 = '//*[@id="plist"]/ul/li[%d]/div/@data-sku' % (num)
            data_scr = e.HTML(res)
            getnum = data_scr.xpath(path2)[0]
            getnum = getnum.strip()
            data_num.append(getnum)
    return data_num

#xpath'/html/body/div[7]/div/div[2]/div[1]/text()'
#req-res-html-data

def getdata(data_num):
    data_1 = {}
    list_1 = []
    no_item = 1
    for item in data_num:
        url1 = 'https://item.jd.com/'+ item +'.html'
        url2 = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds=' + item
        url3 = 'https://p.3.cn/prices/mgets?skuIds=' + 'J_' + item
        req_1 = request.Request(url1,headers=headers)
        res_1 = opener.open(req_1).read().decode('gbk','ignore')

        req_2 = request.Request(url2,headers=headers)
        res_2 = opener.open(req_2).read().decode('utf-8','ignore')

        req_3 = request.Request(url3,headers=headers)
        res_3 = opener.open(req_3).read().decode()

        #提取名字、评论数
        path_name = '//*[@id="detail"]/div[2]/div[1]/div[1]/ul[3]/li[1]/text()'
        path_brand = '//*[@id="parameter-brand"]/li/a/text()'
        html_1 = e.HTML(res_1)
        data_name = html_1.xpath(path_name)
        data_brand = html_1.xpath(path_brand)
        if len(data_name) ==1 :
            comment = json.loads(res_2)['CommentsCount'][0]['GoodRateShow']
            comment_count = json.loads(res_2)['CommentsCount'][0]['CommentCount']
            price = json.loads(res_3)[0]['op']
            data_1[u'商品ID'] = item
            data_1[u'商品名称'] = data_name[0].split('：',1)[1]
            data_1[u'商品价格'] = price[:-3]
            data_1[u'排序'] = no_item
            data_1[u'商品品牌'] = data_brand[0]
            data_1[u'商品好评'] = str(comment) + '%'
            data_1[u'商品总评数'] = comment_count
            no_item += 1
            list_1.append(data_1)
            data_1 = {}
        else:
            continue
    return list_1


#分布率
def getbrand(list_1):
    brand_all = []
    brand_list = []
    brand_num = {}
    #获取所有品牌
    for item in list_1:
        brand_all.append(item[u'商品品牌'])
        if item[u'商品品牌'] in brand_list:
            continue
        else:
            brand_list.append(item[u'商品品牌'])
    #品牌产品份额
    for num in range(len(brand_list)):
        brand_num[brand_list[num]] = brand_all.count(brand_list[num])
    return brand_list,brand_num

#各品牌产品销量加总
def getsale(list_1):
    brand_list = []
    brand_sale = {}
    # 获取所有品牌
    for item in list_1:
        if item[u'商品品牌'] in brand_list:
            continue
        else:
            brand_list.append(item[u'商品品牌'])
    for no in range(len(brand_list)):
        sale = 0
        if no in range(len(brand_list)):

            for num in range(len(list_1)):

                if brand_list[no]==list_1[num][u'商品品牌']:
                    sale += list_1[num][u'商品总评数']
                    brand_sale[brand_list[no]] = sale
                else:
                    brand_sale[brand_list[no]] = sale
        else:
            break
    return brand_sale


data_num = gethtml(5)    ##number here can change the pages you want to get

list_1 = getdata(data_num)

brand_list, brand_num = getbrand(list_1)

brand_sale = getsale(list_1)

print(u'总列表:',list_1)

print(u'品牌数量:',brand_num)

print(u'品牌列表:',brand_list)

print(u'品牌销量:',brand_sale)

#画图

salesort = sorted(brand_sale.items(), key=lambda d:d[1], reverse=True)  #降序

labels = []

number = []

countnum = 0

for num in range(10):

    labels.append(salesort[num][0])

    number.append(salesort[num][1])

    countnum += int(salesort[num][1])

print(countnum)

fig = plt.figure()
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.pie(number,labels=labels, autopct='%.2f%%')
plt.title("分布率",FontProperties = 'STKAITI',fontsize = 24)
plt.axis('equal')
plt.legend(labels=labels,bbox_to_anchor=(1.05, 1), loc='best', borderaxespad=0., fontsize= 40)
plt.show()
plt.savefig("Piephone.jpg")
