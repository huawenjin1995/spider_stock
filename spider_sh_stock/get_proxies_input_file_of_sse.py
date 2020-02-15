import os

def getProxiesInputFile():
    os.system("python3 /home/huawenjin/MyProjects/PycharmProjects/Stock/Proxies-master/run.py -o 'sse.prox.txt'")
    os.system("python3 /home/huawenjin/MyProjects/PycharmProjects/Stock/Proxies-master/run.py -f 'sse.prox.txt' -u 'http://www.sse.com.cn/' -o 'my_prox.txt' ")


if __name__ == '__main__':
    getProxiesInputFile()