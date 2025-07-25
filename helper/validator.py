# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     _validators
   Description :   定义proxy验证方法
   Author :        JHao
   date：          2021/5/25
-------------------------------------------------
   Change Activity:
                   2023/03/10: 支持带用户认证的代理格式 username:password@ip:port
-------------------------------------------------
"""
__author__ = 'JHao'

import re
from requests import head
from util.six import withMetaclass
from util.singleton import Singleton
from handler.configHandler import ConfigHandler

conf = ConfigHandler()

HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
          'Accept': '*/*',
          'Connection': 'keep-alive',
          'Accept-Language': 'zh-CN,zh;q=0.8'}

IP_REGEX = re.compile(r"(.*:.*@)?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}")


class ProxyValidator(withMetaclass(Singleton)):
    pre_validator = []
    http_validator = []
    https_validator = []
    socks5_validator = []  # 新增：SOCKS5验证器列表
    socks4_validator = []  # 新增：SOCKS4验证器列表
    
     # 新增SOCKS5验证器装饰器
    @classmethod
    def addSocks5Validator(cls, func):
        cls.socks5_validator.append(func)
        return func        
    # 新增SOCKS4验证器装饰器
    @classmethod
    def addSocks4Validator(cls, func):
        cls.socks4_validator.append(func)
        return func   
    @classmethod
    def addPreValidator(cls, func):
        cls.pre_validator.append(func)
        return func

    @classmethod
    def addHttpValidator(cls, func):
        cls.http_validator.append(func)
        return func

    @classmethod
    def addHttpsValidator(cls, func):
        cls.https_validator.append(func)
        return func


@ProxyValidator.addPreValidator
def formatValidator(proxy):
    """检查代理格式"""
    return True if IP_REGEX.fullmatch(proxy) else False


@ProxyValidator.addHttpValidator
def httpTimeOutValidator(proxy):
    """ http检测超时 """

    proxies = {"http": "http://{proxy}".format(proxy=proxy), "https": "https://{proxy}".format(proxy=proxy)}

    try:
        r = head(conf.httpUrl, headers=HEADER, proxies=proxies, timeout=conf.verifyTimeout)
        return True if r.status_code == 200 else False
    except Exception as e:
        return False


@ProxyValidator.addHttpsValidator
def httpsTimeOutValidator(proxy):
    """https检测超时"""

    proxies = {"http": "http://{proxy}".format(proxy=proxy), "https": "https://{proxy}".format(proxy=proxy)}
    try:
        r = head(conf.httpsUrl, headers=HEADER, proxies=proxies, timeout=conf.verifyTimeout, verify=False)
        return True if r.status_code == 200 else False
    except Exception as e:
        return False


@ProxyValidator.addHttpValidator
def customValidatorExample(proxy):
    """自定义validator函数，校验代理是否可用, 返回True/False"""
    return True
@ProxyValidator.addSocks5Validator
def socks5TimeOutValidator(proxy):
    """SOCKS5检测超时"""
    # 构建SOCKS5代理格式（支持带认证的代理：username:password@ip:port）
    proxies = {
        "http": f"socks5://{proxy}",
        "https": f"socks5://{proxy}"
    }
    try:
        # 使用配置的HTTP验证地址测试SOCKS5代理
        r = head(conf.httpUrl, headers=HEADER, proxies=proxies, timeout=conf.verifyTimeout,verify=False)
        return True if r.status_code == 200 else False
    except Exception as e:
        return False
@ProxyValidator.addSocks4Validator
def socks4TimeOutValidator(proxy):
    """SOCKS4检测超时"""
    # 构建SOCKS4代理格式（支持带认证的代理：username:password@ip:port）
    proxies = {
        "http": f"socks4://{proxy}",
        "https": f"socks4://{proxy}"
    }
    try:
        # 使用配置的HTTP验证地址测试SOCKS5代理
        r = head(conf.httpUrl, headers=HEADER, proxies=proxies, timeout=conf.verifyTimeout)
        return True if r.status_code == 200 else False
    except Exception as e:
        return False