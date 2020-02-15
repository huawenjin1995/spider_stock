import requests, json, logging, random


class Response():
    def __init__(self, url, prox_inputfile='/home/huawenjin/MyProjects/PycharmProjects/Stock/SPIDER/spider_sz_stock/my_prox.txt'):
        self.url = url
        self.prox_inputfile = prox_inputfile
        self.stockTypes = ('tab1','tab2')   #‘table1’：A股， ‘table2’：B股
        self.headers= {}
        self.params = {}


    @classmethod
    def getProxies(cls,prox_inputfile):
        proxies = []
        with open(prox_inputfile) as file:
            for prox in file:
                prox = prox.split('/')[2].rstrip('\n')
                proxies.append(dict(http=prox))
        return proxies


    @classmethod
    def getResponse(cls,url,my_prox, stockType, page):
        try:
            my_headers = cls.make_headers()
            my_params = cls.make_params(stockType, page)
            # print(my_prox)
            r = requests.get(url,headers= my_headers,params= my_params, proxies= my_prox, timeout=3)
            if r.status_code == 200:
                return r
        except Exception as e:
            logging.error(e)
            return


    @classmethod
    def make_headers(cls):
        headers = {
            "Accept":"application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding":"gzip, deflate",
            "Accept-Language":"zh-CN,zh;q=0.9",
            "Connection":"close",
            "Content-Type":"application/json",
            "Host":"www.szse.cn",
            "Referer":"http://www.szse.cn/market/stock/list/index.html",
            "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
            "X-Request-Type":"ajax",
            "X-Requested-With":"XMLHttpRequest0.3945.88 Safari/537.36"
        }
        return headers

    @classmethod
    def make_params(cls, stockType, page):
        params = {
            "SHOWTYPE":"JSON",
            "CATALOGID":"1110",
            "TABKEY":stockType,                                         #‘table1’：A股， ‘table2’：B股
            "PAGENO":str(page),
            "random":"0.022929621193198413"
        }
        return params

    # @classmethod
    # def getPageCount(cls, response):
    #     '''
    #
    #     :param response:
    #     :return:总页数
    #     '''
    #     if response.text:
    #         stock_info = json.loads(response.text)
    #         page_count = stock_info[0]['metadata']['pagecount']
    #         return page_count




    def getStockList(self):
        stock_datalist = []
        my_proxlist = self.getProxies(self.prox_inputfile)              #获取代理列表
        try:
            for (stockType,pageCount) in [('tab1',110),('tab2',3)]:     # ‘tab1’：A股， ‘tab2’：B股
                # page=1
                # response = cls.getResponse(url, stockType, page, cls.make_headers, cls.make_params)
                # print(response.status_code)
                # print(response.text)
                # page_count = cls.getPageCount(response)
                # logging.info('stockType: %s\tpage_count: %s' %(stockType,page_count))

                # print((stockType,pageCount))
                page = 1
                while page <= pageCount:
                    my_prox = random.choice(my_proxlist)                #随机挑选代理
                    # print(my_prox)
                    response = self.getResponse(self.url,my_prox, stockType, page)
                    if not response:
                        my_proxlist.remove(my_prox)
                        continue
                    if stockType == 'tab1':                             #A股
                        data = json.loads(response.text)[0]['data']
                        # print(data)
                        stock_datalist += (self.getStockInfo(data, stockType))
                        page += 1

                    if stockType == 'tab2':                             #B股
                        data = json.loads(response.text)[1]['data']
                        # print(data)
                        stock_datalist += (self.getStockInfo(data, stockType))
                        page += 1
                    if len(stock_datalist) % 100 == 0:
                        logging.info('get stocks: %s' % len(stock_datalist))
                    # print(stock_datalist)
                    # print('-'*100)

        except Exception as e:
            logging.error(e)

        with open('sz_stocklist.txt', 'w') as file:
            for stock in stock_datalist:
                file.write(str(stock)+'\n')
        return stock_datalist


    @classmethod
    def getStockInfo(cls,data, stockType):
        '''
        :param stock_list:[{tab1:[{stock1}, {stock2}, ...]}, {tab2:[{stock1}, {stock2}, ...]},...]
        :return: 返回stock_info_list:[(公司代码， 公司简称 ，股票代码，简称， 所属板块，上市时间, A/B股)]
        '''
        result = []
        for stock in data:
            if stockType == 'tab1':                                         #A股
                ab = 'A'
                # print(stock)
                comp_abbr = stock['gsjc'].split('<u>')[1].split('<')[0]     #公司简称
                stock_info = {'comp_code' : stock['zqdm'], 'comp_abbr':comp_abbr, 'stock_code' : stock['agdm'],
                                'stock_abbr' : stock['agjc'], 'date' : stock['agssrq'], 'indust' : stock['sshymc'],
                                'attr_info':ab}
                result.append(stock_info)
            if stockType == 'tab2':                                         #B股
                ab = 'B'
                comp_abbr = stock['gsjc'].split('<u>')[1].split('<')[0]     #公司简称
                stock_info = {'comp_code': stock['zqdm'], 'comp_abbr': comp_abbr, 'stock_code': stock['bgdm'],
                                'stock_abbr': stock['bgjc'], 'date': stock['bgssrq'], 'indust': stock['sshymc'],
                                'attr_info': ab}
                result.append(stock_info)
        # print(result)
        return result


if __name__ == '__main__':

    logging.basicConfig(
        filename='spider_sz_stock.log',
        level=logging.INFO,
        format='%(asctime)s [%(threadName)s] [%(name)s] [%(levelname)s] %(filename)s[line:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # r = requests.get('http://www.szse.cn/api/report/ShowReport/data',
    #                  headers={
    #                      "Accept":"application/json, text/javascript, */*; q=0.01",
    #                      "Accept-Encoding":"gzip, deflate",
    #                      "Accept-Language":"zh-CN,zh;q=0.9",
    #                      "Connection":"keep-alive",
    #                      "Content-Type":"application/json",
    #                      "Host":"www.szse.cn",
    #                      "Referer":"http://www.szse.cn/market/stock/list/index.html",
    #                      "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    #                      "X-Request-Type":"ajax",
    #                      "X-Requested-With":"XMLHttpRequest0.3945.88 Safari/537.36"
    #                  },
    #                  params={
    #                      "SHOWTYPE":"JSON",
    #                      "CATALOGID":"1110",
    #                      "TABKEY":'tab2',  # ‘tab1’：A股， ‘tab2’：B股， ‘tab3’：A+B股
    #                      "PAGENO":'2',
    #                      "random":"0.9595490043641028"
    #                  }
    #                 )




    # print('-' * 100)
    # stock_info = json.loads(r.text)
    # # print(stock_info)
    # page_count = stock_info[1]['metadata']['pagecount']
    # print(page_count, type(page_count))
    # data = stock_info[1]['data']
    #
    # for stock in data:
    #     print(stock)


    r = Response('http://www.szse.cn/api/report/ShowReport/data')
    sz_stock_list = r.getStockList()
    print(len(sz_stock_list))
    for stock in sz_stock_list:
        print(stock)

    # proxice = []
    # with open('/home/huawenjin/MyProjects/PycharmProjects/Stock/Proxies-master/my_prox.txt','r') as file:
    #     for prox in file:
    #         prox = prox.split('/')[2].rstrip('\n')
    #         # print(prox)
    #         proxice.append(dict(http=prox))
    #
    # # my_prox = random.choice(proxice)
    # print(proxice)




