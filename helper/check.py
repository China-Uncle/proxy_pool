# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     check
   Description :   执行代理校验
   Author :        JHao
   date：          2019/8/6
-------------------------------------------------
   Change Activity:
                   2019/08/06: 执行代理校验
                   2021/05/25: 分别校验http和https
                   2022/08/16: 获取代理Region信息
-------------------------------------------------
"""
__author__ = 'JHao'

from util.six import Empty
from threading import Thread
from datetime import datetime
from util.webRequest import WebRequest
from handler.logHandler import LogHandler
from helper.validator import ProxyValidator
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler


class DoValidator(object):
    """ 执行校验 """

    conf = ConfigHandler()

    @classmethod
    def validator(cls, proxy, work_type):
        """
        校验入口
        Args:
            proxy: Proxy Object
            work_type: raw/use
        Returns:
            Proxy Object
        """
        https_r = False
        socks5_r = False
        socks4_r = False
        http_r = False
        proxy.last_status = False
        #如果proxy.source 包含socks4则使用socks4校验
        if "Socks4" in proxy.source:
             proxy.last_status = cls.socks4Validator(proxy)
             proxy.link_type = "socks4"
             proxy.socks4 = True
        elif "Socks5" in proxy.source:
            # 新增：SOCKS5验证
             proxy.last_status = cls.socks5Validator(proxy)
             proxy.link_type = "socks5"
             proxy.socks5 = True
        else:
            http_r = cls.httpValidator(proxy)
            https_r = False if not http_r else cls.httpsValidator(proxy) 
            proxy.link_type = "http" if https_r else "https"
            proxy.last_status = http_r
            proxy.https = True if https_r else False
        proxy.check_count += 1
        proxy.last_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # proxy.last_status = True if http_r or socks5_r or socks4_r else False
        if proxy.last_status:
            if proxy.fail_count > 0:
                proxy.fail_count -= 1 
            if work_type == "raw":
                proxy.region = cls.regionGetter(proxy) if cls.conf.proxyRegion else ""
        else:
            proxy.fail_count += 1
        return proxy

    @classmethod
    def httpValidator(cls, proxy):
        for func in ProxyValidator.http_validator:
            if not func(proxy.proxy):
                return False
        return True
    # 新增：SOCKS5验证方法
    @classmethod
    def socks5Validator(cls, proxy):
        for func in ProxyValidator.socks5_validator:
            if not func(proxy.proxy):
                return False
        return True
    # 新增：SOCKS4验证方法
    @classmethod
    def socks4Validator(cls, proxy):
        for func in ProxyValidator.socks4_validator:
            if not func(proxy.proxy):
                return False
        return True
    @classmethod
    def httpsValidator(cls, proxy):
        for func in ProxyValidator.https_validator:
            if not func(proxy.proxy):
                return False
        return True

    @classmethod
    def preValidator(cls, proxy):
        for func in ProxyValidator.pre_validator:
            if not func(proxy):
                return False
        return True

    @classmethod
    def regionGetter(cls, proxy):
        try:
            url = 'https://searchplugin.csdn.net/api/v1/ip/get?ip=%s' % proxy.proxy.split(':')[0]
            r = WebRequest().get(url=url, retry_time=1, timeout=2).json
            return r['data']['address']
        except:
            return 'error'


class _ThreadChecker(Thread):
    """ 多线程检测 """

    def __init__(self, work_type, target_queue, thread_name):
        Thread.__init__(self, name=thread_name)
        self.work_type = work_type
        self.log = LogHandler("checker")
        self.proxy_handler = ProxyHandler()
        self.target_queue = target_queue
        self.conf = ConfigHandler()

    def run(self):
        self.log.info("{}ProxyCheck - {}: start".format(self.work_type.title(), self.name))
        while True:
            try:
                proxy = self.target_queue.get(block=False)
            except Empty:
                self.log.info("{}ProxyCheck - {}: complete".format(self.work_type.title(), self.name))
                break
            proxy = DoValidator.validator(proxy, self.work_type)
            if self.work_type == "raw":
                self.__ifRaw(proxy)
            else:
                self.__ifUse(proxy)
            self.target_queue.task_done()

    def __ifRaw(self, proxy):
        if proxy.last_status:
            if self.proxy_handler.exists(proxy):
                self.log.info('RawProxyCheck - {}: {}: {} exist'.format(self.name,proxy.source, proxy.proxy.ljust(23)))
            else:
                self.log.info('RawProxyCheck - {}: {}: {} pass'.format(self.name,proxy.source, proxy.proxy.ljust(23)))
                self.proxy_handler.put(proxy)
        else:
            self.log.info('RawProxyCheck - {}: {}:  {} fail'.format(self.name,proxy.source, proxy.proxy.ljust(23)))

    def __ifUse(self, proxy):
        if proxy.last_status:
            self.log.info('UseProxyCheck - {}: {}:  {} pass'.format(self.name,proxy.source, proxy.proxy.ljust(23)))
            self.proxy_handler.put(proxy)
        else:
            if proxy.fail_count > self.conf.maxFailCount:
                self.log.info('UseProxyCheck - {}: {}:  {} fail, count {} delete'.format(self.name,proxy.source,
                                                                                    proxy.proxy.ljust(23),
                                                                                    proxy.fail_count))
                self.proxy_handler.delete(proxy)
            else:
                self.log.info('UseProxyCheck - {}: {}:  {} fail, count {} keep'.format(self.name,proxy.source,
                                                                                  proxy.proxy.ljust(23),
                                                                                  proxy.fail_count))
                self.proxy_handler.put(proxy)


def Checker(tp, queue):
    """
    run Proxy ThreadChecker
    :param tp: raw/use
    :param queue: Proxy Queue
    :return:
    """
    thread_list = list()
    for index in range(20):
        thread_list.append(_ThreadChecker(tp, queue, "thread_%s" % str(index).zfill(2)))

    for thread in thread_list:
        thread.setDaemon(True)
        thread.start()

    for thread in thread_list:
        thread.join()
