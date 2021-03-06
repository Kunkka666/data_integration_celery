#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author  : MG
@Time    : 2019/2/26 17:38
@File    : __init__.py.py
@contact : mmmaaaggg@163.com
@desc    : 
"""
from tasks.backend import bunch_insert
from tasks.config import config
import jqdatasdk
import logging
from sqlalchemy.types import String, Date

logger = logging.getLogger(__name__)
HAS_AUTHORIZED = False
AUTHORIZED_SUCC = False


def check_before_run(check_func):

    import functools

    def func_wrapper(target_func):

        @functools.wraps(target_func)
        def call_func(*args, **kwargs):
            is_ok = check_func()
            if is_ok:
                return target_func(*args, **kwargs)
            else:
                raise ImportError('jqdatasdk 授权失败')

        return call_func

    return func_wrapper


def auth_once():
    global HAS_AUTHORIZED, AUTHORIZED_SUCC
    if not HAS_AUTHORIZED:
        try:
            jqdatasdk.auth(config.JQ_USERNAME, config.JQ_PASSWORD)
            AUTHORIZED_SUCC = True
            logger.info('jqdatasdk.auth 授权成功')
        except:
            AUTHORIZED_SUCC = False
            logger.exception("jqdatasdk 授权异常")
        finally:
            HAS_AUTHORIZED = True

    return AUTHORIZED_SUCC


finance = jqdatasdk.finance
valuation = jqdatasdk.valuation


@check_before_run(auth_once)
def get_trade_days(*args, **kwargs):
    return jqdatasdk.get_trade_days(*args, **kwargs)


@check_before_run(auth_once)
def get_all_securities(*args, **kwargs):
    return jqdatasdk.get_all_securities(*args, **kwargs)


@check_before_run(auth_once)
def get_price(*args, **kwargs):
    return jqdatasdk.get_price(*args, **kwargs)


@check_before_run(auth_once)
def get_all_trade_days(*args, **kwargs):
    return jqdatasdk.get_all_trade_days(*args, **kwargs)


@check_before_run(auth_once)
def query(*args, **kwargs):
    return jqdatasdk.query(*args, **kwargs)


@check_before_run(auth_once)
def get_fundamentals(*args, **kwargs):
    return jqdatasdk.get_fundamentals(*args, **kwargs)


def import_info_table(type_name):
    """
    调用 get_all_securities 获取指定 type 的信息
    type: 'stock', 'fund', 'index', 'futures', 'etf', 'lof', 'fja', 'fjb'。types为空时返回所有股票, 不包括基金,指数和期货
    :param type_name:
    :return:
    """
    table_name = f'jq_{type_name}_info'
    logging.info("更新 %s 开始", table_name)
    # has_table = engine_md.has_table(table_name)
    param_list = [
        ('jq_code', String(20)),
        ('display_name', String(20)),
        ('name', String(20)),
        ('start_date', Date),
        ('end_date', Date),
    ]
    # 设置 dtype
    dtype = {key: val for key, val in param_list}

    # 数据提取
    # types: list: 用来过滤securities的类型, list元素可选:
    # 'stock', 'fund', 'index', 'futures', 'etf', 'lof', 'fja', 'fjb'。types为空时返回所有股票, 不包括基金,指数和期货
    # date: 日期, 一个字符串或者 [datetime.datetime]/[datetime.date] 对象,
    # 用于获取某日期还在上市的股票信息. 默认值为 None, 表示获取所有日期的股票信息
    stock_info_all_df = get_all_securities(types=type_name)
    stock_info_all_df.index.rename('jq_code', inplace=True)
    stock_info_all_df.reset_index(inplace=True)

    logging.info('%s 数据将被导入', stock_info_all_df.shape[0])
    data_count = bunch_insert(stock_info_all_df, table_name=table_name, dtype=dtype, primary_keys=['jq_code'])
    logging.info("更新 %s 完成 存量数据 %d 条", table_name, data_count)
