import logging, requests
from SPIDER.spider_sh_stock.spider_sh_stocklist import Response

class DetailResponse(Response):
    def __init__(self, url, productid_list):
        self.prod_id = productid_list
        self.url = url
        self.headers= {}
        self.params = {}


    @classmethod
    def getResponse(cls, url, productid):
        try:
            my_headers = cls.make_headers()
            my_params = cls.make_params(productid)
            r = requests.get(url, headers = my_headers, params=my_params)
            if r.status_code == 200:
                return r
        except Exception as e:
            logging.error(e)

    @classmethod
    def make_params(cls, productid):
        params = {
            "jsonCallBack":"jsonpCallback66604",
            "isPagination":"false",
            "sqlId":"COMMON_SSE_ZQPZ_GP_GPLB_C",
            "productid":productid,
            "_":"1578207903851"
        }
        return params


    def getStockDetailList(self):
        result = []
        company = set()
        count = 0
        for productid in self.prod_id:
            if productid not in company:
                # print(productid)
                productid = int(productid)
                response = self.getResponse(self.url, productid)
                # print(response.text)
                from_jsonp = self.dealJsonp(response.text, _jsonp_begin=r'jsonpCallback66604(', _jsonp_end=r')')
                # print(from_jsonp)
                if 'result' in from_jsonp:
                    # print('-' * 100)
                    stock_info = from_jsonp['result'][0]
                stock_details = self.getStockInfo(stock_info)
                result.append(stock_details)
                count += 1
                company.add(productid)
            if count % 100 == 0:
                logging.info('get stocks: %s' % count)

        with open('sh_stockdetails.txt', 'w') as file:
            for stock in result:
                file.write(str(stock) + '\n')
        return result
            # print('-'*100)


    @classmethod
    def getStockInfo(cls, stock):
        '''
        :param stock_info: 包含股票信息的字典
        :return: 返回stock_info_list:每只股票的详细信息
        '''
        # print(stock)
        stock_info = {'comp_code': stock['COMPANY_CODE'], 'comp_area': stock['AREA_NAME_DESC'],
                        'comp_addr': stock['COMPANY_ADDRESS'], 'legal': stock['LEGAL_REPRESENTATIVE'],
                        'stock_codeA' : stock['SECURITY_CODE_A'],'stock_codeB': stock['SECURITY_CODE_B'],
                        'status':stock['STATE_CODE_A_DESC'], 'SSE_code':stock['SSE_CODE_DESC'],
                        'office_zip':stock['OFFICE_ZIP'], 'comp_fullname':stock['FULLNAME'],
                        'e-mail':stock['E_MAIL_ADDRESS'], 'csrc':stock['CSRC_GREAT_CODE_DESC'],
                        'www_addr':stock['WWW_ADDRESS'], 'CSRC_code':stock['CSRC_CODE_DESC'],
                        'office_addr':stock['OFFICE_ADDRESS']}

        return stock_info





if __name__ == '__main__':
    logging.basicConfig(
        filename='spider_sh_stock.log',
        level=logging.INFO,
        format='%(asctime)s [%(threadName)s] [%(name)s] [%(levelname)s] %(filename)s[line:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    productid_list = []
    with open('sh_stock_list.txt') as file:
        for line in file:
            comp_code = (line.split(',')[0].split(':')[1])
            comp_code = comp_code.replace("'",'')
            productid_list.append(comp_code)

    # productid_list = ['688388', '688389', '688399']
    print(len(productid_list))
    r_stock_detail = DetailResponse('http://query.sse.com.cn/commonQuery.do', productid_list)
    stock_detail_list = r_stock_detail.getStockDetailList()
    print(len(stock_detail_list))

    # for stock in stock_detail_list:
    #     print('-' * 100)
    #     print(stock)
