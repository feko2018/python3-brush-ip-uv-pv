# python3-brush-ip-uv-pv
- 这是一个基于高并发模式来刷网站ip \ uv \ pv量的python3脚本！
# 脚本构成
- python3-get-proxy-ip.py ##刷ip/uv/pv量脚本，基于python3.6
- blogs_url.txt  ##用于存储要刷的url，一行一条
- ipporxy.txt    ##可以为空，用户存储网站获取到的有效代理ip的日志
- success_ip.txt ##可以为空，用户存储刷新成功的代理ip和url的日志
# 脚本简单说明
基本流程：
- 先从免费代理网站获取到ip列表
- 过滤有效ip，通过ip端口判断是否有效
- 有效ip循环去curl访问网页，记录日志
- 采用了多进程并发来获取ip列表和执行访问网页
