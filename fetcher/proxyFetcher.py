# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyFetcher
   Description :
   Author :        JHao
   date：          2016/11/25
-------------------------------------------------
   Change Activity:
                   2016/11/25: proxyFetcher
-------------------------------------------------
"""
__author__ = 'JHao'

import re
import json
from time import sleep

from util.webRequest import WebRequest


class ProxyFetcher(object):
    """
    proxy getter
    """

    @staticmethod
    def freeProxy01():
        """
        站大爷 https://www.zdaye.com/dayProxy.html
        """
        start_url = "https://www.zdaye.com/dayProxy.html"
        html_tree = WebRequest().get(start_url, verify=False).tree
        latest_page_time = html_tree.xpath("//span[@class='thread_time_info']/text()")[0].strip()
        from datetime import datetime
        interval = datetime.now() - datetime.strptime(latest_page_time, "%Y/%m/%d %H:%M:%S")
        if interval.seconds < 300:  # 只采集5分钟内的更新
            target_url = "https://www.zdaye.com/" + html_tree.xpath("//h3[@class='thread_title']/a/@href")[0].strip()
            while target_url:
                _tree = WebRequest().get(target_url, verify=False).tree
                for tr in _tree.xpath("//table//tr"):
                    ip = "".join(tr.xpath("./td[1]/text()")).strip()
                    port = "".join(tr.xpath("./td[2]/text()")).strip()
                    yield "%s:%s" % (ip, port)
                next_page = _tree.xpath("//div[@class='page']/a[@title='下一页']/@href")
                target_url = "https://www.zdaye.com/" + next_page[0].strip() if next_page else False
                sleep(5)

    @staticmethod
    def freeProxy02():
        """
        代理66 http://www.66ip.cn/
        """
        url = "http://www.66ip.cn/"
        resp = WebRequest().get(url, timeout=10).tree
        for i, tr in enumerate(resp.xpath("(//table)[3]//tr")):
            if i > 0:
                ip = "".join(tr.xpath("./td[1]/text()")).strip()
                port = "".join(tr.xpath("./td[2]/text()")).strip()
                yield "%s:%s" % (ip, port)

    @staticmethod
    def freeProxy03():
        """ 开心代理 """
        target_urls = ["http://www.kxdaili.com/dailiip.html", "http://www.kxdaili.com/dailiip/2/1.html"]
        for url in target_urls:
            tree = WebRequest().get(url).tree
            for tr in tree.xpath("//table[@class='active']//tr")[1:]:
                ip = "".join(tr.xpath('./td[1]/text()')).strip()
                port = "".join(tr.xpath('./td[2]/text()')).strip()
                yield "%s:%s" % (ip, port)

    @staticmethod
    def freeProxy04():
        """ FreeProxyList https://www.freeproxylists.net/zh/ """
        url = "https://www.freeproxylists.net/zh/?c=CN&pt=&pr=&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=50"
        tree = WebRequest().get(url, verify=False).tree
        from urllib import parse

        def parse_ip(input_str):
            html_str = parse.unquote(input_str)
            ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', html_str)
            return ips[0] if ips else None

        for tr in tree.xpath("//tr[@class='Odd']") + tree.xpath("//tr[@class='Even']"):
            ip = parse_ip("".join(tr.xpath('./td[1]/script/text()')).strip())
            port = "".join(tr.xpath('./td[2]/text()')).strip()
            if ip:
                yield "%s:%s" % (ip, port)

    @staticmethod
    def freeProxy05(page_count=1):
        """ 快代理 https://www.kuaidaili.com """
        url_pattern = [
            'https://www.kuaidaili.com/free/inha/{}/',
            'https://www.kuaidaili.com/free/intr/{}/'
        ]
        url_list = []
        for page_index in range(1, page_count + 1):
            for pattern in url_pattern:
                url_list.append(pattern.format(page_index))

        for url in url_list:
            tree = WebRequest().get(url).tree
            proxy_list = tree.xpath('.//table//tr')
            sleep(1)  # 必须sleep 不然第二条请求不到数据
            for tr in proxy_list[1:]:
                yield ':'.join(tr.xpath('./td/text()')[0:2])

    @staticmethod
    def freeProxy06():
        """ 冰凌代理 https://www.binglx.cn """
        url = "https://www.binglx.cn/?page=1"
        try:
            tree = WebRequest().get(url).tree
            proxy_list = tree.xpath('.//table//tr')
            for tr in proxy_list[1:]:
                yield ':'.join(tr.xpath('./td/text()')[0:2])
        except Exception as e:
            print(e)

    @staticmethod
    def freeProxy07():
        """ 云代理 """
        urls = ['http://www.ip3366.net/free/?stype=1', "http://www.ip3366.net/free/?stype=2"]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ":".join(proxy)

    @staticmethod
    def freeProxy08():
        """ 小幻代理 """
        urls = ['https://ip.ihuan.me/address/5Lit5Zu9.html']
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(r'>\s*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*?</a></td><td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ":".join(proxy)

    @staticmethod
    def freeProxy09(page_count=1):
        """ 免费代理库 """
        for i in range(1, page_count + 1):
            url = 'http://ip.jiangxianli.com/?country=中国&page={}'.format(i)
            html_tree = WebRequest().get(url, verify=False).tree
            for index, tr in enumerate(html_tree.xpath("//table//tr")):
                if index == 0:
                    continue
                yield ":".join(tr.xpath("./td/text()")[0:2]).strip()

    @staticmethod
    def freeProxy10():
        """ 89免费代理 """
        r = WebRequest().get("https://www.89ip.cn/index_1.html", timeout=10)
        proxies = re.findall(
            r'<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>[\s\S]*?(\d+)[\s\S]*?</td>',
            r.text)
        for proxy in proxies:
            yield ':'.join(proxy)

    @staticmethod
    def freeProxy11():
        """ 稻壳代理 https://www.docip.net/ """
        r = WebRequest().get("https://www.docip.net/data/free.json", timeout=10)
        try:
            for each in r.json['data']:
                yield each['ip']
        except Exception as e:
            print(e)

    @staticmethod
    def freeProxy12():
        """ https://github.com/monosans/proxy-list """
        r = WebRequest().get("https://github.com/monosans/proxy-list/raw/refs/heads/main/proxies/http.txt", timeout=10)
        try:
            for line in r.text:
                ip = line.split(':')[0]
                port = line.split(':')[1]
                yield f"{ip}:{port}"  # 返回host:port格式
        except Exception as e:
            print(e)

    @staticmethod
    def freeProxy13():
        """ https://github.com/TheSpeedX/PROXY-List """
        r = WebRequest().get("https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt", timeout=10)
        try:
            for line in r.text:
                ip = line.split(':')[0]
                port = line.split(':')[1]
                yield f"{ip}:{port}"  # 返回host:port格式
        except Exception as e:
            print(e)
    @staticmethod
    def Socks5Proxy01():
        """示例：采集支持SOCKS5的代理源https://github.com/TheSpeedX/PROXY-List"""
        url = "https://github.com/TheSpeedX/PROXY-List/raw/refs/heads/master/socks5.txt"  # 替换为实际SOCKS5代理源
        try:
            #内容为每行一个IP:端口 
            tree = WebRequest().get(url)
            for line in tree.text.splitlines():
                ip = line.split(':')[0]
                port = line.split(':')[1]
                yield f"{ip}:{port}"  # 返回host:port格式
        except Exception as e:
            print(f"采集SOCKS5代理失败: {e}")
    @staticmethod
    def Socks4Proxy01():
        """示例：采集支持SOCKS4的代理源https://github.com/TheSpeedX/PROXY-List"""
        url = "https://github.com/TheSpeedX/PROXY-List/raw/refs/heads/master/socks4.txt"  # 替换为实际SOCKS5代理源
        try:
            #内容为每行一个IP:端口 
            tree = WebRequest().get(url)
            for line in tree.text.splitlines():
                ip = line.split(':')[0]
                port = line.split(':')[1]
                yield f"{ip}:{port}"  # 返回host:port格式
        except Exception as e:
            #获取方法名
            func_name = sys._getframe().f_code.co_name
            print(f"{func_name}采集代理失败: {e}")
    @staticmethod
    def Socks5Proxy02():
        """示例：采集支持SOCKS4的代理源https://github.com/fyvri/fresh-proxy-list?tab=readme-ov-file"""
        url = "https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/socks5.txt"  # 替换为实际SOCKS5代理源
        try:
            #内容为每行一个IP:端口 
            tree = WebRequest().get(url)
            for line in tree.text.splitlines():
                ip = line.split(':')[0]
                port = line.split(':')[1]
                yield f"{ip}:{port}"  # 返回host:port格式
        except Exception as e:
            #获取方法名
            func_name = sys._getframe().f_code.co_name
            print(f"{func_name}采集代理失败: {e}")
    @staticmethod
    def Socks5Proxy03():
        """示例：采集支持SOCKS5的代理源
        https://github.com/gfpcom/free-proxy-list/tree/main/list
        """
        url = "https://raw.githubusercontent.com/gfpcom/free-proxy-list/refs/heads/main/list/socks5.txt"  # 替换为实际SOCKS5代理源
        try:
            #内容为每行一个IP:端口 
            tree = WebRequest().get(url)
            for line in tree.text.splitlines():
                #内容为socks5://001.224.3.122:3888 
                line = line.replace('socks5://', '')
                ip = line.split(':')[0]
                port = line.split(':')[1]
                yield f"{ip}:{port}"  # 返回host:port格式
        except Exception as e:
            #获取方法名
            func_name = sys._getframe().f_code.co_name
            print(f"{func_name}采集代理失败: {e}")
    @staticmethod
    def Socks5Proxy04():
        """示例：采集支持SOCKS5的代理源
        https://github.com/xing2kong/fresh-proxy-list--?utm_source=chatgpt.com
        """
        url = "https://vakhov.github.io/fresh-proxy-list/socks5.txt"  # 替换为实际SOCKS5代理源
        try:
            #内容为每行一个IP:端口 
            tree = WebRequest().get(url)
            for line in tree.text.splitlines():
                ip = line.split(':')[0]
                port = line.split(':')[1]
                yield f"{ip}:{port}"  # 返回host:port格式
        except Exception as e:
            #获取方法名
            func_name = sys._getframe().f_code.co_name
            print(f"{func_name}采集代理失败: {e}")
    @staticmethod
    def Socks4Proxy02():
        """示例：采集支持SOCKS4的代理源https://github.com/fyvri/fresh-proxy-list?tab=readme-ov-file"""
        url = "https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/socks4.txt"  # 替换为实际SOCKS5代理源
        try:
            #内容为每行一个IP:端口 
            tree = WebRequest().get(url)
            for line in tree.text.splitlines():
                ip = line.split(':')[0]
                port = line.split(':')[1]
                yield f"{ip}:{port}"  # 返回host:port格式
        except Exception as e:
            #获取方法名
            func_name = sys._getframe().f_code.co_name
            print(f"{func_name}采集代理失败: {e}")
    @staticmethod
    def Socks4Proxy03():
        """示例：采集支持SOCKS4的代理源
        https://github.com/gfpcom/free-proxy-list/tree/main/list
        """
        url = "https://raw.githubusercontent.com/gfpcom/free-proxy-list/refs/heads/main/list/socks4.txt"  # 替换为实际SOCKS5代理源
        try:
            #内容为每行一个IP:端口 
            tree = WebRequest().get(url)
            for line in tree.text.splitlines():
                line = line.replace('socks4://', '')
                ip = line.split(':')[0]
                port = line.split(':')[1]
                yield f"{ip}:{port}"  # 返回host:port格式
        except Exception as e:
            #获取方法名
            func_name = sys._getframe().f_code.co_name
            print(f"{func_name}采集代理失败: {e}")   
    @staticmethod
    def Socks4Proxy04():
        """示例：采集支持SOCKS4的代理源
        https://github.com/xing2kong/fresh-proxy-list--?utm_source=chatgpt.com
        """
        url = "https://vakhov.github.io/fresh-proxy-list/socks4.txt"  # 替换为实际SOCKS5代理源
        try:
            #内容为每行一个IP:端口 
            tree = WebRequest().get(url)
            for line in tree.text.splitlines(): 
                ip = line.split(':')[0]
                port = line.split(':')[1]
                yield f"{ip}:{port}"  # 返回host:port格式
        except Exception as e:
            #获取方法名
            func_name = sys._getframe().f_code.co_name
            print(f"{func_name}采集代理失败: {e}")  
    @staticmethod
    def HttpsProxy01():
        """示例：采集支持SOCKS4的代理源https://github.com/fyvri/fresh-proxy-list?tab=readme-ov-file"""
        url = "https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/https.txt"  # 替换为实际SOCKS5代理源
        try:
            #内容为每行一个IP:端口 
            tree = WebRequest().get(url)
            for line in tree.text.splitlines():
                ip = line.split(':')[0]
                port = line.split(':')[1]
                yield f"{ip}:{port}"  # 返回host:port格式
        except Exception as e:
            #获取方法名
            func_name = sys._getframe().f_code.co_name
            print(f"{func_name}采集代理失败: {e}") 
    @staticmethod
    def HttpsProxy02():
        """示例：采集支持HTTPS的代理源
        https://github.com/gfpcom/free-proxy-list/tree/main/list
        """
        url = "https://raw.githubusercontent.com/gfpcom/free-proxy-list/refs/heads/main/list/https.txt"  # 替换为实际SOCKS5代理源
        try:
            #内容为每行一个IP:端口 
            tree = WebRequest().get(url)
            for line in tree.text.splitlines():
                ip = line.split(':')[0]
                port = line.split(':')[1]
                yield f"{ip}:{port}"  # 返回host:port格式
        except Exception as e:
            #获取方法名
            func_name = sys._getframe().f_code.co_name
            print(f"{func_name}采集代理失败: {e}")
            
   


if __name__ == '__main__':
    p = ProxyFetcher()
    for _ in p.freeProxy06():
        print(_)

# http://nntime.com/proxy-list-01.htm
