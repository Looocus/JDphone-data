# -*- coding:UTF-8 -*-

import requests, re, json
from matplotlib import pyplot as plt
#from lxml import etree
#import http.cookiejar


##初始页面
#kw = input('查询什么:')
#初始参数
header = {

    'accept-encoding' : 'gzip, deflate, br',
    'accept-language' : 'en-US,en;q=0.9',
    'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    'Referer' : 'https://www.taobao.com/',

}
#start_url = 'https://s.taobao.com/search?q=' + kw + '&imgfile=&commend=all&search_type=item&ie=utf8&psort=_lw_quantity&s='
start_url = 'https://s.taobao.com/search?q=手机&imgfile=&commend=all&search_type=item&ie=utf8&psort=_lw_quantity&s='

true = "True"
false = "False"

s = requests.session()
s.keep_alive = False

def get_pagesize(url):

    print(url)

    scr = requests.get(url, headers = header).content.decode('UTF-8')
    #js获取 g_page_config =
    js_path = re.compile(r'g_page_config = (.*?);\n', re.S)

    js_text = re.findall(js_path, scr)[0]

    pagecount = re.search(r'"totalPage":(\d+?),', js_text)

    pagecount = int(pagecount.group(1))

    pagesize = re.search(r'"pageSize":(\d+?),', js_text)

    pagesize = int(pagesize.group(1))

    return pagesize, pagecount, js_text

def get_phdata(text):

    text = json.loads(text)

    ph_data = text['mods']['grid']['data']['spus']

    return ph_data

#翻页操作
def get_nextpage(pagesize, pagecount):

    page_list = []

    for num in range(pagecount):

        url = start_url + str(pagesize*num)

        page_list.append(url)

    return page_list

def get_right(ph_list):

    f = open('Taobao.json', 'w')

    for item in ph_list:

        f.write(json.dumps(dict(item), ensure_ascii=False) + ',\n')

    f.close()

def salesort(brand_list, ph_list):

    sale_list = []

    sale = 0

    for name in brand_list:

        for item in ph_list:

            if name in item['ph_name']:

                sale += item['ph_monthsale']

        sale_list.append(sale)

        sale = 0

    return sale_list

def sortedsale(brand_list, sale_list): #归类排序

    sale_dict = {}

    for num in range(len(brand_list)):

        sale_dict[brand_list[num]] = int(sale_list[num])

    print(sale_dict)

    sale_sorted = sorted(sale_dict.items(), key = lambda d:d[1], reverse=True) #降序

    return sale_sorted

def showpic(sorted_dict):  #降序才可用

    labels = []

    number = []

    countnum = 0

    for num in range(4):

        labels.append(sorted_dict[num][0])

        number.append(sorted_dict[num][1])

        countnum += int(sorted_dict[num][1])

    print(countnum)

    fig = plt.figure()
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.pie(number, labels=labels, autopct='%.2f%%')
    plt.title("分布率", FontProperties='STKAITI', fontsize=24)
    plt.axis('equal')
    plt.legend(labels=labels, bbox_to_anchor=(1.05, 1), loc='best', borderaxespad=0., fontsize=18)
    plt.show()
    plt.savefig("Piephone.jpg")

if __name__ == '__main__':

    #页码停止，当三页内都没有所需item，即刻停止

    item_num = []

    pagesize, pagecount, js_text = get_pagesize(start_url)

    page_list = get_nextpage(pagesize, pagecount)

    print(page_list)

    ph_list = []

    show_page = 1

    check = input('是否筛选小米,Y/N:')

    check = check.lower()

    for url in page_list:

        try :

            pagesize, pagecount, js_text = get_pagesize(url)

        except UnicodeDecodeError :

            print('编码问题，跳过')

            show_page += 1

            continue

        else:

            pass

        ph_data = get_phdata(js_text)

        for num in range(len(ph_data)):

            ph_dict = {}

            ph_dict['ph_name'] = ph_data[num]['title']

            ph_dict['ph_price'] = int(ph_data[num]['price'])

            ph_dict['ph_seller'] = int(ph_data[num]['seller']['num'])

            ph_dict['ph_monthsale'] = int(ph_data[num]['month_sales'])

            ph_dict['ph_size'] = ph_data[num]['importantKey']

            if ph_dict['ph_monthsale'] == 0 or ph_dict['ph_seller'] == 0:

                continue

            elif re.findall(r'屏(\d+?).(\d+?)\"', ph_dict['ph_size'], re.S):

                pass

            else:

                continue

            if check == 'y':

                if re.findall(u'小米', ph_dict['ph_name']):

                    ph_list.append(ph_dict)

                else:

                    continue

            else:

                ph_list.append(ph_dict)

        print('正在爬取第', show_page, '页', ',爬取了', len(ph_list), '个数据')

        item_num.append(len(ph_list))

        if item_num.count(len(ph_list)) == 3 :

            print('已无符合条件商品')

            break

        else:

            pass

        show_page += 1

    get_right(ph_list)  #ph_list 是list

    brand_list = []

    for item in ph_list:

        if len(re.findall(r'(.*?) ', item['ph_name'])) >= 1:

            if re.search(r'(.*?) ', item['ph_name']).group(1) in brand_list:

                continue

            else:

                brand_list.append(re.search(r'(.*?) ', item['ph_name']).group(1))

                continue

        else:

            if item['ph_name'] in brand_list:

                continue

            else:

                brand_list.append(item['ph_name'])

                continue

    sale_list = salesort(brand_list, ph_list)

    sale_sorted = sortedsale(brand_list, sale_list)

    price_pre = {}

    price_pre['999以下'] = 0

    price_pre['1000-1999'] = 0

    price_pre['2000-2499'] = 0

    price_pre['2500以上'] = 0

    for item in ph_list:

        if "小米" in item['ph_name']:

            if item['ph_price'] <= 999:

                price_pre['999以下'] += item['ph_monthsale']

            if item['ph_price'] <= 1999 and item['ph_price'] >=1000:

                price_pre['1000-1999'] += item['ph_monthsale']

            if item['ph_price'] <= 2499 and item['ph_price'] >= 2000:

                price_pre['2000-2499'] += item['ph_monthsale']

            if item['ph_price'] >= 2500:

                price_pre['2500以上'] += item['ph_monthsale']

    price_pre = sorted(price_pre.items(), key = lambda d:d[1], reverse=True)

    showpic(price_pre)