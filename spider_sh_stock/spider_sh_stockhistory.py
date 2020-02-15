import logging, requests, arrow, random
from datetime import datetime
from SPIDER.spider_sh_stock.spider_sh_stocklist import Response

class PriceResponce(Response):
    def __init__(self,url, found_stocklist, end_date):
        self.url = url
        self.found_stocklist = found_stocklist
        self.end_date = end_date


    # @classmethod
    # def getProxies(cls, prox_inputfile):
    #     proxies = []
    #     with open(prox_inputfile) as file:
    #         for prox in file:
    #             prox = prox.split('/')[2].rstrip('\n')
    #             proxies.append(dict(http=prox))
    #     return proxies

    @classmethod
    def getResponse(cls, url, found_id, date):
        my_headers = cls.make_headers()
        my_params = cls.make_params(found_id, date)
        try:
            r = requests.get(url, headers= my_headers, params=my_params)
            if r.status_code == 200:
                return r
        except Exception as e:
            logging.error(e)
            return

    @classmethod
    def make_params(cls, found_id, date):
        params = {
            "jsonCallBack": "jsonpCallback86036",
            "FUNDID": found_id,     #股票代码
            "inMonth": "",
            "inYear": "",
            "searchDate":date,
            "_": "1578276953942"
        }
        return params

    @classmethod
    def getDateList(cls,start_date, end_date):
        '''

        :param start_date: 开始日期，例如：‘2015-01-25’
        :param end_date: 截止日期，例如：‘2020-01-06’
        :return: 返回开始日期——截止日期间的所有工作日(周一到周五）
        '''

        start = datetime.strptime(start_date, '%Y-%m-%d')
        # print(start)
        end = datetime.strptime(end_date, '%Y-%m-%d')
        date_list = []
        if start > end:
            return date_list
        else:
            for r in arrow.Arrow.range('day', start, end):
                date = arrow.get(r).format('YYYY-MM-DD')
                if datetime.strptime(date, '%Y-%m-%d').weekday() not in (5, 6):
                    date_list.append(date)
                # print(date)
                # print(type(date))
            return date_list


    def getStockTradeList(self):
        result = []
        try:
            for (stock_code, stock_date) in self.found_stocklist:
                logging.info('begin to craw history-trade of stock: %s' % stock_code)
                # print(stock_code)
                # print(stock_date)
                stock_code = int(stock_code)
                found_id = stock_code
                date_list = self.getDateList(stock_date,self.end_date)
                if date_list:   #日期列表非空
                    for date in date_list:
                        # print(date)
                        stock_date_trade = self.getStockInfo(self.url, found_id, date)
                        if stock_date_trade:     #有交易信息
                            # print(stock_date_trade)
                            result.append(stock_date_trade)
                            if len(result) % 100 == 0:
                                logging.info('get history-trade success for %s days ' % len(result))
                        else:  #非交易日
                            continue
                logging.info('get history trade success for stock: %s' % found_id)
        except Exception as e:
            logging.error(e)

        with open('sh_stock_history_trade.txt','w') as file:
            for stock in result:
                file.write(str(stock) + '\n')
        return result



    @classmethod
    def getStockInfo(cls,url, found_id,date):
        '''
        :param found_id: 公司代码
        :return: 返回每个元素为每只股票每天股价信息
        '''
        # prox_list = prox_list
        # while True:
        #     if prox_list == []:
        #         logging.info('no proxies to use')
        #         return
        #     prox = random.choice(prox_list)
        #     response = cls.getResponse(url, found_id,date, prox)
        #     if response:        #请求成功
        #         break
        #     if not response:    #请求失败，继续更换代理
        #         prox_list.remove(prox)
        #         continue
        # # print(response.text)

        response = cls.getResponse(url, found_id, date)
        if response:    #请求成功
            stock_date_info = cls.dealJsonp(response.text, _jsonp_begin=r'jsonpCallback86036(', _jsonp_end=r')')['result'][0]   #获取交易信息
        # print(stock_date_info)

            if stock_date_info["closeMarketValue"] > 0:
                stock_info = dict(id=stock_date_info['id'], productName=stock_date_info['productName'], #代码， 名称
                                    closeMarketValue=stock_date_info['closeMarketValue'],   #收盘总市值（万元）
                                    closeNegoValue=stock_date_info['closeNegoValue'], openPrice=stock_date_info['openPrice'], #流通市值（万元），开盘价（元）
                                    closePrice=stock_date_info['closePrice'], closeTrTx=stock_date_info['closeTrTx'], #收盘价(元），成交笔数（万笔）
                                    closeTrVol=stock_date_info['closeTrVol'], closeTrAmt=stock_date_info['closeTrAmt'],   #成交金额（万元），成交量（万股）
                                    tradeDate=date)
                return stock_info
        else:   #请求失败
            return







if __name__ == '__main__':
    logging.basicConfig(
        filename='spider_sh_stock.log',
        level=logging.INFO,
        format='%(asctime)s [%(threadName)s] [%(name)s] [%(levelname)s] %(filename)s[line:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


    stock_list = []
    with open('sh_stock_list.txt') as file:
        for line in file:
            # print(line)
            comp_code = (line.split(',')[0].split(':')[1])
            comp_code = comp_code.replace("'", '')
            date = (line.split(',')[6].split(':')[1].split('}')[0])
            date = date.replace("'",'')
            date = date.replace(' ','')
            # print(date)
            stock_list.append((comp_code, date))
    # print(stock_list)

    r_price = PriceResponce('http://query.sse.com.cn/security/fund/queryNewAllQuatAbel.do', stock_list,'2020-01-09')
    stock_pricelist = r_price.getStockTradeList()
    print(len(stock_pricelist))
