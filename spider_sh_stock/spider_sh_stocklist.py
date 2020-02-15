import requests, json, logging


class Response():
    def __init__(self, url):
        self.url = url
        self.headers= {}
        self.params = {}

    @classmethod
    def getResponse(cls,url, stockType, make_headers, make_params):
        try:
            my_headers = make_headers()
            my_params = make_params(stockType)
            r = requests.get(url, headers = my_headers, params=my_params)
            if r.status_code == 200:
                return r
        except Exception as e:
            logging.error(e)

    @classmethod
    def make_headers(cls):
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "h-CN,zh;q=0.9",
            "Connection": "close",
            "Host": "query.sse.com.cn",
            "Referer": "http://www.sse.com.cn/assortment/stock/list/share/",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
        }
        return headers

    @classmethod
    def make_params(cls, stockType, beginPage="1", pageSize="2000", endPage="60"):
        params = {
            "jsonCallBack": "jsonpCallback88226",
            "isPagination": "true",
            "stockCode": "",
            "csrcCode": "",
            "areaName": "",
            "stockType": stockType,     # '1':主板A股， ’2‘：主板B股， ’8‘：科创板
            "pageHelp.cacheSize": "1",
            "pageHelp.beginPage": beginPage,
            "pageHelp.pageSize": pageSize,
            "pageHelp.pageNo": "1",
            "pageHelp.endPage": endPage,
        }
        return params

    @classmethod
    def dealJsonp(cls, jsonp_str, _jsonp_begin=r'jsonpCallback88226(', _jsonp_end=r')'):
        '''
        :param jsonp_str:爬取到的jsonp字符串
        :param _jsonp_begin: jsonp字符串开头的‘jsonCallBack(’， ps:'jsonCallBack'为params参数中jsonCallBack对应的值
        :param _jsonp_end: jsonp字符串结尾，一般为')'
        :return:返回json解析后的对象
        '''
        jsonp_str = jsonp_str.strip()
        if not jsonp_str.startswith(_jsonp_begin) or \
                not jsonp_str.endswith(_jsonp_end):
            raise ValueError('Invalid JSONP')
        return json.loads(jsonp_str[len(_jsonp_begin):-len(_jsonp_end)])

    @classmethod
    def getStockList(cls, url, stockTypeList):
        stock_in_type = []
        try:
            for stockType in stockTypeList:  # '1':主板A股， ’2‘：主板B股， ’8‘：科创板
                response = cls.getResponse(url, stockType, cls.make_headers, cls.make_params)
                # print(type(self.dealJsonp(response.text)))
                stock_in_type.append(cls.dealJsonp(response.text))
                # print(stock_in_type)
                # print('-'*100)
            return stock_in_type
        except Exception as e:
            logging.error(e)

    def getStockInfoList(self):
        '''
        :param json_dict:json解析后得到的字典，其中的一个键为'pageHelp',对应的value为一个dict, 该dic 其中包含一对('data'-> [{stock1_info} ,{stock2_info}...])
        :return:返回一个列表[{stock1_info} ,{stock2_info}...]
        '''
        stock_in_type = self.getStockList(self.url, stockTypeList=('1','2','8')) # '1':主板A股， ’2‘：主板B股， ’8‘：科创板

        stock_info_list = []
        if stock_in_type:  #非空
            for json_dict in stock_in_type:
                # print(json_dict)
                # print('-' * 100)
                if 'pageHelp' in json_dict:
                    include_data_dict = json_dict['pageHelp']
                    # print(include_data_dict['data']) #include_data_dict['data']: [{stock1_info}, {stock2_info},...]
                    # print('-' * 100)
                    stock_info_list += (include_data_dict['data'])   #stock_info_list: [include_data_dict1, include_data_dict2,...]
        # print(len(stock_info_list))
        if stock_info_list:
            total_stock_info = self.getStockInfo(stock_info_list)
            with open('sh_stock_list.txt','w') as file:
                for stock in total_stock_info:
                    file.write(str(stock) + '\n')
            return total_stock_info


    @classmethod
    def getStockInfo(cls,stock_list):
        '''
        :param stock_list:每个元素为包含股票信息的字典
        :return: 返回stock_info_list:[(公司代码， 公司简称 ，股票代码，简称，A/B, 所属板块，上市时间)]
        '''
        result = []
        company = set()
        for stock in stock_list:
            if stock['COMPANY_CODE'] not in company:
                comp_code = stock['COMPANY_CODE']        #公司代码
                comp_abbr = stock['COMPANY_ABBR']        #公司简称
                board = stock['LISTING_BOARD']           # '0':主板， '1':科创板,  '
                date = stock['LISTING_DATE']             #上市时间
                if stock['SECURITY_CODE_A'] != '-' and stock['SECURITY_CODE_B'] != '-':  # A+B股
                    stock_code = stock['SECURITY_CODE_A']
                    stock_abbr = stock['SECURITY_ABBR_A']
                    ab = "A"
                    stock_info = {"comp_code" : comp_code, "comp_abbr":comp_abbr, "stock_code" : stock_code,
                              "stock_abbr" : stock_abbr,"attr_info":ab, "board" : board, "date" : date}
                    result.append(stock_info)
                    stock_code = stock['SECURITY_CODE_B']
                    stock_abbr = stock['SECURITY_ABBR_B']
                    ab = "B"
                    stock_info = {"comp_code": comp_code, "comp_abbr": comp_abbr, "stock_code": stock_code,
                                  "stock_abbr": stock_abbr, "attr_info": ab, "board": board, "date": date}
                    result.append(stock_info)
                    company.add(stock['COMPANY_CODE'])

                else:  #A/B 股
                    stock_code = stock['SECURITY_CODE_A'] if stock['SECURITY_CODE_A'] != '-' else stock['SECURITY_CODE_B']
                    stock_abbr = stock['SECURITY_ABBR_A'] if stock['SECURITY_ABBR_A'] != '-' else stock['SECURITY_ABBR_B']
                    ab = "A" if stock['SECURITY_CODE_A'] != '-' else "B"
                    stock_info = {"comp_code": comp_code, "comp_abbr": comp_abbr, "stock_code": stock_code,
                                  "stock_abbr": stock_abbr, "attr_info": ab, "board": board, "date": date}
                    result.append(stock_info)
                    company.add(stock['COMPANY_CODE'])
        return result

from collections import namedtuple

ColumRecord = namedtuple("ColumRecord",["field_type","column_name","field_value"])

def trans_dict(stock_dict_list):
    result = []
    for stock_dict in stock_dict_list:
        list_column = []
        for info in stock_dict:
            col = ColumRecord('string', info, stock_dict[info])
            list_column.append(col)
        result.append(list_column)
    return result



if __name__ == '__main__':
    logging.basicConfig(
        filename='spider_sh_stock.log',
        level=logging.INFO,
        format='%(asctime)s [%(threadName)s] [%(name)s] [%(levelname)s] %(filename)s[line:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )



    r = Response("http://query.sse.com.cn/security/stock/getStockListData2.do")
    stock_list = r.getStockInfoList()
    # print(len(stock_list))
    # stock_B = []
    # for stock in stock_list:
    #     if stock['attr_info'] == 'B':
    #         stock_B.append(stock)
    #         print(stock)
    # print(len(stock_B))

    # stock_list_records = trans_dict(stock_B[:2])
    # print(stock_list_records)
    # print(trans_dict(stock_list_records))
