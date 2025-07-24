# -*- coding: utf-8 -*-
"""
-----------------------------------------------------
   File Name：     redisClient.py
   Description :   封装Redis相关操作
   Author :        JHao
   date：          2019/8/9
------------------------------------------------------
   Change Activity:
                   2019/08/09: 封装Redis相关操作
                   2020/06/23: 优化pop方法, 改用hscan命令
                   2021/05/26: 区别http/https代理
------------------------------------------------------
"""
__author__ = 'JHao'

from redis.exceptions import TimeoutError, ConnectionError, ResponseError
from redis.connection import BlockingConnectionPool
from handler.logHandler import LogHandler
from random import choice
from redis import Redis
import json


class RedisClient(object):
    """
    Redis client

    Redis中代理存放的结构为hash：
    key为ip:port, value为代理属性的字典;

    """

    def __init__(self, **kwargs):
        """
        init
        :param host: host
        :param port: port
        :param password: password
        :param db: db
        :return:
        """
        self.name = ""
        kwargs.pop("username")
        self.__conn = Redis(connection_pool=BlockingConnectionPool(decode_responses=True,
                                                                   timeout=5,
                                                                   socket_timeout=5,
                                                                   **kwargs))

    def get(self, https):
        """
        返回一个代理
        :return:
        """
        if https:
            items = self.__conn.hvals(self.name)
            proxies = list(filter(lambda x: json.loads(x).get("https"), items))
            return choice(proxies) if proxies else None
        else:
            proxies = self.__conn.hkeys(self.name)
            proxy = choice(proxies) if proxies else None
            return self.__conn.hget(self.name, proxy) if proxy else None

    def put(self, proxy_obj):
        """
        将代理放入hash, 使用changeTable指定hash name
        :param proxy_obj: Proxy obj
        :return:
        """
        data = self.__conn.hset(self.name, proxy_obj.proxy, proxy_obj.to_json)
        return data

    def pop(self, https):
        """
        弹出一个代理
        :return: dict {proxy: value}
        """
        proxy = self.get(https)
        if proxy:
            self.__conn.hdel(self.name, json.loads(proxy).get("proxy", ""))
        return proxy if proxy else None

    def delete(self, proxy_str):
        """
        移除指定代理, 使用changeTable指定hash name
        :param proxy_str: proxy str
        :return:
        """
        return self.__conn.hdel(self.name, proxy_str)

    def exists(self, proxy_str):
        """
        判断指定代理是否存在, 使用changeTable指定hash name
        :param proxy_str: proxy str
        :return:
        """
        return self.__conn.hexists(self.name, proxy_str)

    def update(self, proxy_obj):
        """
        更新 proxy 属性
        :param proxy_obj:
        :return:
        """
        return self.__conn.hset(self.name, proxy_obj.proxy, proxy_obj.to_json)

    def getAll(self, https):
        """
        字典形式返回所有代理, 使用changeTable指定hash name
        :return:
        """
        items = self.__conn.hvals(self.name)
        if https:
            return list(filter(lambda x: json.loads(x).get("https"), items))
        else:
            return items

    def clear(self):
        """
        清空所有代理, 使用changeTable指定hash name
        :return:
        """
        return self.__conn.delete(self.name)

    def getCount(self):
        """
        返回代理数量
        :return:
        """
        proxies = self.getAll(https=False)
        return {'total': len(proxies), 'https': len(list(filter(lambda x: json.loads(x).get("https"), proxies)))}

    def changeTable(self, name):
        """
        切换操作对象
        :param name:
        :return:
        """
        self.name = name

    def test(self):
        log = LogHandler('redis_client')
        try:
            self.getCount()
        except TimeoutError as e:
            log.error('redis connection time out: %s' % str(e), exc_info=True)
            return e
        except ConnectionError as e:
            log.error('redis connection error: %s' % str(e), exc_info=True)
            return e
        except ResponseError as e:
            log.error('redis connection error: %s' % str(e), exc_info=True)
            return e

def get_by_socks4(self):
    """获取一个支持socks4的代理"""
    items = self.__conn.hvals(self.name)
    # 筛选出socks4=True的代理
    proxies = list(filter(lambda x: json.loads(x).get("socks4"), items))
    return choice(proxies) if proxies else None

def pop_by_socks4(self):
    """取出并删除一个支持socks4的代理"""
    items = self.__conn.hvals(self.name)
    proxies = list(filter(lambda x: json.loads(x).get("socks4"), items))
    if proxies:
        proxy = choice(proxies)
        proxy_dict = json.loads(proxy)
        self.__conn.hdel(self.name, proxy_dict["proxy"])
        return proxy
    return None

def get_all_by_socks4(self):
    """获取所有支持socks4的代理"""
    items = self.__conn.hvals(self.name)
    return list(filter(lambda x: json.loads(x).get("socks4"), items))





def get_by_socks4(self):
    """获取一个支持socks4的代理"""
    items = self.__conn.hvals(self.name)
    # 筛选出socks5=true的代理
    proxies = list(filter(lambda x: json.loads(x).get("socks4"), items))
    return choice(proxies) if proxies else none

def pop_by_socks5(self):
    """取出并删除一个支持socks5的代理"""
    items = self.__conn.hvals(self.name)
    proxies = list(filter(lambda x: json.loads(x).get("socks5"), items))
    if proxies:
        proxy = choice(proxies)
        proxy_dict = json.loads(proxy)
        self.__conn.hdel(self.name, proxy_dict["proxy"])
        return proxy
    return none

def get_all_by_socks5(self):
    """获取所有支持socks5的代理"""
    items = self.__conn.hvals(self.name)
    return list(filter(lambda x: json.loads(x).get("socks5"), items))
