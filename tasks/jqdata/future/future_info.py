#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author  : MG
@Time    : 19-4-19 下午2:56
@File    : future_info.py
@contact : mmmaaaggg@163.com
@desc    : 
"""
from tasks.jqdata import import_info_table
from tasks import app


@app.task
def import_jq_future_info(chain_param=None, refresh=False):
    """ 获取全市场股票代码及名称
    """
    import_info_table('futures')


if __name__ == "__main__":
    import_jq_future_info()
