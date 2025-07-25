'''
Date: 2025-07-24 11:04:34
LastEditors: 马艳龙 myl86898244@gmail.com
LastEditTime: 2025-07-25 11:40:15
FilePath: \proxy_pool\handler\proxyHandler.py
'''
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ProxyHandler.py
   Description :
   Author :       JHao
   date：          2016/12/3
-------------------------------------------------
   Change Activity:
                   2016/12/03:
                   2020/05/26: 区分http和https
-------------------------------------------------
"""
__author__ = 'JHao'

from helper.proxy import Proxy
from db.dbClient import DbClient
from handler.configHandler import ConfigHandler


class ProxyHandler(object):
    """ Proxy CRUD operator"""

    def __init__(self):
        self.conf = ConfigHandler()
        self.db = DbClient(self.conf.dbConn)
        self.db.changeTable(self.conf.tableName)

    def get(self, https=False, socks5=False, socks4=False):
        """
        return a proxy
        Args:
            https: True/False
        Returns:
        """
        proxy = self.db.get(https,socks5, socks4) 
        return Proxy.createFromJson(proxy) if proxy else None

    def pop(self, https, socks5=False, socks4=False):
        """
        return and delete a useful proxy
        :return:
        """
        proxy = self.db.pop(https,socks5, socks4)
        if proxy:
            return Proxy.createFromJson(proxy)
        return None

    def put(self, proxy):
        """
        put proxy into use proxy
        :return:
        """
        self.db.put(proxy)

    def delete(self, proxy):
        """
        delete useful proxy
        :param proxy:
        :return:
        """
        return self.db.delete(proxy.proxy)

    def getAll(self, https=False, socks5=False, socks4=False):
        """
        get all proxy from pool as Proxy list
        :return:
        """
      
        proxies = self.db.getAll(https,socks5,socks4)
        return [Proxy.createFromJson(_) for _ in proxies]

    def exists(self, proxy):
        """
        check proxy exists
        :param proxy:
        :return:
        """
        return self.db.exists(proxy.proxy)

    def getCount(self):
        """
        return raw_proxy and use_proxy count
        :return:
        """
        total_use_proxy = self.db.getCount()
        return {'count': total_use_proxy}
