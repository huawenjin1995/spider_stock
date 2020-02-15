from SPIDER.spider_sz_stock.spider_sz_stocklist import Response
import requests, logging, json, random
from GRPC.server_and_client.prox.getprox_client import getprox
from GRPC.server_and_client.prox.getprox_client import deleteIP

class DetailResponse(Response):
    def __init__(self,url, stocklist, prox_input_file='/home/huawenjin/MyProjects/PycharmProjects/Stock/SPIDER/spider_sz_stock/my_prox.txt'):
        self.url = url
        self.stocklist = stocklist
        self.prox_input_file = prox_input_file
        self.headers = {}
        self.params = {}

    @classmethod
    def getResponse(cls,url, stockCode, my_prox):
        try:
            my_headers = cls.make_headers()
            my_params = cls.make_params(stockCode)
            r = requests.get(url,headers= my_headers,params= my_params, proxies=my_prox, timeout=5)
            if r.status_code == 200:
                return r
        except Exception as e:
            logging.error(e)
            return

    @classmethod
    def make_params(cls, stockCode):
        params = {
            "random":"0.022929621193198413",
            "secCode":stockCode
        }
        return params


    def getStockDetails(self):
        result = []
        prox_list = self.getProxies(self.prox_input_file)

        for stockcode in self.stocklist:
            # print(stockcode)
            while True:
                # my_prox = random.choice(prox_list)
                prox = getprox()
                my_prox = dict(http = prox)
                # print(my_prox)
                response = self.getResponse(self.url, stockcode, my_prox)
                # print(response.text)
                if response:        #请求成功
                    break
                if not response:    #请求失败
                    deleteIP(prox)
                    continue
                # if prox_list == []: #代理列表为空
                #     logging.info('no proxies to use')
                #     break
            try:
                stock_info = self.getInfo(stockcode,response)
                result.append(stock_info)
                logging.info('get stock: %s' %stockcode)
                if len(result) % 100 == 0:
                    logging.info('get stocks: %s' %len(result))
            except Exception as e:
                logging.error('failed get stock: %s\t error: %s' %(stockcode,e))

        with open('spider_sz_stockdetails.txt','w') as file:
            for stock in result:
                file.write(str(stock)+'\n')
        return result

    @classmethod
    def getInfo(cls,stockcode, response):
        from_json = json.loads(response.text)
        data = from_json['data']            #data: {stock_data}
        if stockcode == data['agdm']:       #A股
            stock_abbr = data['agjc']
            date = data['agssrq']           #上市日期
            capital = data['agzgb']         #总股本（万股）
            circu_capital = data['agltgb']  #流通股本（万股）
        if stockcode == data['bgdm']:       #B股
            stock_abbr = data['bgjc']
            date = data['bgssrq']
            capital = data['bgzgb']         #总股本（万股）
            circu_capital = data['bgltgb']  #流通股本（万股）
        comp_name = data['gsqc']
        addr = data['zcdz']                 #注册地址
        indust = data['sshymc']             #所属行业
        off_web = data['http']              #官网

        result = {
            'stockcode':stockcode, 'stock_abbr':stock_abbr,'comp_name':comp_name,
            'date':date, 'capital':capital, 'circu_capital':circu_capital,
            'addr':addr, 'indust':indust, 'off_web':off_web
        }
        return result



if __name__ == '__main__':
    logging.basicConfig(
        filename='spider_sz_stock.log',
        level=logging.INFO,
        format='%(asctime)s [%(threadName)s] [%(name)s] [%(levelname)s] %(filename)s[line:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # r = requests.get('http://www.szse.cn/api/report/index/companyGeneralization',
    #                  headers={
    #                      "Accept":"application/json, text/javascript, */*; q=0.01",
    #                      "Accept-Encoding":"gzip, deflate",
    #                      "Accept-Language":"zh-CN,zh;q=0.9",
    #                      "Connection":"close",
    #                      "Content-Type":"application/json",
    #                      "Host":"www.szse.cn",
    #                      "Referer":"http://www.szse.cn/market/stock/list/index.html",
    #                      "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    #                      "X-Request-Type":"ajax",
    #                      "X-Requested-With":"XMLHttpRequest0.3945.88 Safari/537.36"
    #                  },
    #                  params={
    #                      "random":"0.022929621193198413",
    #                      "secCode":"200761"
    #                  },
    #
    #                 )
    # print(r.status_code)
    # print(r.content.decode('utf-8'))
    # from_json = json.loads(r.text)
    # print(from_json)
    # print(from_json['data'])


    stockcode_list = []
    with open('/home/huawenjin/MyProjects/PycharmProjects/Stock/SPIDER/spider_sz_stock/sz_stocklist.txt') as file:
        for line in file:
            comp_code = (line.split(',')[0].split(':')[1])
            comp_code = comp_code.replace("'",'')
            comp_code = comp_code.replace(' ','')
            stockcode_list.append(comp_code)



    # print(len(stockcode_list))

    r_stockdetail = DetailResponse('http://www.szse.cn/api/report/index/companyGeneralization', stockcode_list)
    stockdetail_list = r_stockdetail.getStockDetails()

    # for stock in stockdetail_list:
        # print(stock)


