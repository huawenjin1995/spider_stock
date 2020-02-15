import os

def getProxiesInputFile():
    os.system('python3 /home/huawenjin/MyProjects/PycharmProjects/Stock/Proxies-master/run.py ')
    os.system("python3 /home/huawenjin/MyProjects/PycharmProjects/Stock/Proxies-master/run.py -f 'proxies.txt' -u 'http://www.szse.cn' -o 'my_prox.txt' ")


if __name__ == '__main__':
    getProxiesInputFile()