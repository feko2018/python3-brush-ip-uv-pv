#-*-coding:utf-8 -*-

import json,time,requests,datetime,subprocess,random,telnetlib
from multiprocessing import Pool,Manager
from lxml import etree

def rm_symbol(c1):
    new_c1=c1.replace('\n','').replace('\t','')
    return  new_c1
#获取免费代理网站ip(ip+空格+port形式)
def get_89ip_data(i,q):
    url = 'http://www.89ip.cn/index_{}.html'.format(i)
    q.put(url)
    res = requests.get(url)
    res.encoding = 'utf-8'
    html=etree.HTML(res.text)
    ipdress=html.xpath('//table[@class="layui-table"]/tbody/tr/td[1]/text()')
    port=html.xpath('//table[@class="layui-table"]/tbody/tr/td[2]/text()')
    ipdress=list(map(rm_symbol,ipdress))
    port=list(map(rm_symbol,port))
    data=list(zip(ipdress,port))
    for j in range(len(data)):
        ip_is_alive(data[j][0]+' '+data[j][1])

#存活ip检测
def ip_is_alive(ip_port):
    global is_alive
    global not_alive
    ip=ip_port.split(' ')[0]
    port=ip_port.split(' ')[-1]
    try:
        tn = telnetlib.Telnet(ip, port=port,timeout=2)
    except:
        print('[-] ip:{}:{}'.format(ip,port))
        not_alive+=1
    else:
        print('[+] ip:{}:{}'.format(ip,port))
        curl_pv(ip,port) #有效的ip就开始刷pv
        is_alive+=1
        with open('ipporxy.txt','a') as f:
            f.write(ip+':'+port+'\n')

#提取IP池的ip 以列表形式返回
def read_ip(dress):
    with open(dress,'r') as f:
        ip_port=f.read().split('\n')[1:]
        for i in ip_port:
            if i=='':
                ip_port.remove(i)
    return ip_port



##检查到有效ip直接通过curl去访问
def curl_pv(ip,port):
    blogs_url =[]
    try:
        with open('blogs_url.txt', 'r') as f:
            for line in f.readlines():
                line=line.strip()
                blogs_url.append(line)
    except Exception:
        print("没有blogs_url.txt文件")
        exit()

    print('------------开始刷pv/uv------------')
    ##伪装成浏览器
    ua = ['User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
'user-agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36']
    #测试连接
    cmd = "curl -I --connect-timeout 3 -m 10  --proxy   %s:%s  %s  -A '%s'" % (ip,port,"https://www.baidu.com",ua[random.randint(0,2)])
    status = subprocess.call(cmd,shell=True)
    if status == 0:
        for i in range(1,random.randint(2,3)):  ##随机浏览1-2次
            for url in blogs_url:
                print("%s 第%s次成功"%(url,i))
                cmd = "curl --connect-timeout 3 -m 10  --proxy   %s:%s  %s  -A '%s'" % (ip,port,url,ua[random.randint(0,3)])
                status = subprocess.call(cmd,shell=True)
                time.sleep(random.randint(1,3))  ##随机1-3s等待
                if status != 0:
                    break
                else:
                    with open('successful_ip.txt', 'a') as f:
                        f.write(('%s---%s')%(ip,url) + '\n') ##写入成功的url和代理ip
            if status != 0:
                break


if __name__ == "__main__":
    not_alive=0
    is_alive=0
    q = Manager().Queue() ##用于进程池Pool的进程之间的消息队列
    ret = []
    print('------------IP检测开始------------')
    print('[+]代表ip有效\n[-]代表ip无效\n')
    with open('ipporxy.txt', 'w') as f:
        f.write('------------自动获取 IP代理池-----------\n')
    with open('successful_ip.txt', 'w') as f:
        f.write('------------刷ip/uv/pu成功的url和代理ip-----------\n')

    print("开始执行主程序")
    start_time=time.time()
    pool=Pool(20)     # 使用进程池创建20个子进程
    print("开始执行子进程")
    for i in range(1,100):
        pool.apply_async(get_89ip_data, args=(i,q))
    print('======  apply_async	======')
    pool.close() #关闭进程池，不再接受新的进程，只是会把状态改为不可再插入元素的状态
    pool.join()  #主进程阻塞等待子进程的退出
    print("主进程结束耗时%s"%(time.time()-start_time))
    while True:
        if not q.empty():
            value = q.get(True)  # 从消息队列中取出信息
            ret.append(value)
        else:
            break
    with open('ipporxy.txt', 'a') as f:
        f.write('------更新时间：{}-----\n'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
