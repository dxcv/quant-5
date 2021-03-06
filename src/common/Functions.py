# coding: utf-8
"""
@author: 邢不行
微信：xingbx007
小密圈：每天分享、讨论量化的内容，http://t.xiaomiquan.com/BEiqzVB
量化课程（在微信中打开）：https://st.h5.xiaoe-tech.com/st/5mXf4p6se
"""
import pandas as pd  # 导入pandas，我们一般为pandas取一个别名叫做pd
import os

# 导入数据
from common import config

"""
将中文名称映射成训练数据的列名, 有两点好处
1.中文名编程方便
2.如果将来更新训练数据, 列名变了, 只需要修改映射关系即可, 不需要修改代码
"""


def stock_rename_map():
    rename_map = {}
    for k in config.name_map.keys():
        rename_map[config.name_map[k]] = k
        print("'{}': '{}',".format(config.name_map[k], k))

    exit(0)
    return rename_map


def import_stock_data(stock_code, columns=None):
    """
    导入在data/input_data/stock_data下的股票数据。
    :param stock_code: 股票数据的代码，例如'sh600000'
    :param columns: 获取数据列, list结构, 如果为空获取全部列
    :return 单个股票数据
    """
    df = pd.read_csv(config.stock_data_path + stock_code + '.csv', encoding='gbk')

    df = df.rename(columns=config.rename_map)

    if columns and len(columns) >= 0:
        df = df[columns]

    df.sort_values(by=['交易日期'], inplace=True)
    df['交易日期'] = pd.to_datetime(df['交易日期'])

    # df.reset_index(inplace=True, drop=True)
    df.reset_index(inplace=True, drop=True)
    return df


def import_stock_data_by_list(stock_list, start_date, end_date, columns=None, print_progress=False):
    """
    :param stock_list: 股票代码列表
    :param start_date: 获取start_date之后的数据, 包括start_date当天数据
    :param end_date: 获取end_date之前的数据, 包括end_date当天数据
    :param columns: 获取数据列, list结构, 如果为空获取全部列
    :param print_progress: 打印数据导入进度
    :return 返回包含所有股票数据的DataFrame
    """
    pass


def import_index_data(index_code, columns=None):
    """
    导入在data/input_data/stock_data下的股票数据。
    :param index_code: 指数代码，例如'sh000001'
    :param columns: 获取数据列, list结构, 如果为空获取全部列
    若不为默认值，会导入除基础字段之外其他指定的字段
    :return:
    """
    df = pd.read_csv(config.index_data_path + index_code + '.csv', encoding='gbk')

    # columns_list = ['交易日期', '股票代码', '开盘价', '最高价', '最低价', '收盘价', '涨跌幅', '成交额', '成交额'] + other_columns

    # df.columns = [i.encode('utf8') for i in df.columns]
    df = df.rename(columns=config.rename_map)

    if columns and len(columns) >= 0:
        df = df[columns]

    df.sort_values(by=['交易日期'], inplace=True)
    df['交易日期'] = pd.to_datetime(df['交易日期'])

    # df.reset_index(inplace=True, drop=True)
    df.reset_index(inplace=True, drop=True)
    return df


# 导入指数
def import_sh000001_data():
    # 导入指数数据
    df_index = pd.read_csv(config.index_data_path + 'sh000001.csv', parse_dates=['date'])
    df_index = df_index[['date', 'change']]
    df_index.rename(columns={'date': '交易日期', 'change': '大盘涨跌幅'}, inplace=True)
    df_index.sort_values(by=['交易日期'], inplace=True)
    df_index.dropna(subset=['大盘涨跌幅'], inplace=True)
    df_index.reset_index(inplace=True, drop=True)

    return df_index


def get_trade_date_list(start_date, end_date):
    df_index = pd.read_csv(config.index_data_path + 'sh000001.csv', parse_dates=['date'])

    df_index = df_index[(df_index['date'] >= start_date) & (df_index['date'] <= end_date)]
    df_index.sort_values(by='date', inplace=True)
    return list(df_index['date'])


# 计算复权价
def cal_right_price(input_stock_data, right_type='后复权', price_columns=None):
    """
    计算复权价
    :param input_stock_data:
    :param right_type:复权类型，可以是'后复权'或者'前复权'
    :return:
    """
    # 创建空的df
    right_price_df = pd.DataFrame()

    # 计算复权收盘价
    num = {'后复权': 0, '前复权': -1}
    price1 = input_stock_data['收盘价'].iloc[num[right_type]]
    right_price_df['复权因子'] = (1.0 + input_stock_data['涨跌幅']).cumprod()
    price2 = right_price_df['复权因子'].iloc[num[right_type]]
    right_price_df['收盘价'] = right_price_df['复权因子'] * (price1 / price2)

    if not price_columns or len(price_columns) <= 0:
        price_columns = ['开盘价', '最高价', '最低价', '收盘价']

    for c in price_columns:
        if c == '收盘价':
            continue
        right_price_df[c] = input_stock_data[c] / input_stock_data['收盘价'] * right_price_df['收盘价']
    return right_price_df[price_columns]


# 导入某文件夹下所有股票的代码
def get_stock_code_list_in_one_dir(path):
    """
    从指定文件夹下，导入所有csv文件的文件名
    :param path:
    :return:
    """

    stock_list = []

    # 系统自带函数os.walk，用于遍历文件夹中的所有文件
    for root, dirs, files in os.walk(path):
        if files:  # 当files不为空的时候
            for f in files:
                if f.endswith('.csv'):
                    stock_list.append(f[:8])

    return stock_list


# 导入某文件夹下所有股票的代码
def get_stock_code_list():
    """
    从指定文件夹下，导入所有csv文件的文件名
    :param path:
    :return:
    """
    stock_list = []

    # 系统自带函数os.walk，用于遍历文件夹中的所有文件
    for root, dirs, files in os.walk(config.stock_data_path):
        if files:  # 当files不为空的时候
            for f in files:
                if f.endswith('.csv'):
                    stock_list.append(f.split('.csv')[0])

    return stock_list


# 将股票数据和指数数据合并
def merge_with_index_data(df, index_data):
    """
    将股票数据和指数数据合并
    :param df: 股票数据
    :param index_data: 指数数据
    :return:
    """

    # 将股票数据和上证指数合并
    df = pd.merge(left=df, right=index_data, on='交易日期', how='right', sort=True, indicator=True)

    # 将停盘时间的['涨跌幅', '成交额']数据填补为0
    fill_0_list = ['涨跌幅', '成交额']
    df.loc[:, fill_0_list] = df[fill_0_list].fillna(value=0)

    # 用前一天的收盘价，补全收盘价的空值
    df['收盘价'] = df['收盘价'].fillna(method='ffill')

    # 用收盘价补全开盘价、最高价、最低价的空值
    df['开盘价'] = df['开盘价'].fillna(value=df['收盘价'])
    df['最高价'] = df['最高价'].fillna(value=df['收盘价'])
    df['最低价'] = df['最低价'].fillna(value=df['收盘价'])

    # 用前一天的数据，补全其余空值
    df.fillna(method='ffill', inplace=True)

    # 去除上市之前的数据
    df = df[df['股票代码'].notnull()]
    df.reset_index(drop=True, inplace=True)

    # 计算当天是否交易
    df['是否交易'] = 1
    df.loc[df[df['_merge'] == 'right_only'].index, '是否交易'] = 0
    del df['_merge']

    return df


def transfer_to_period_data(df, period_type='m'):
    """

    :param df:
    :param period_type:
    :return:
    """

    # 将交易日期设置为index
    df['周期最后交易日'] = df['交易日期']
    df.set_index('交易日期', inplace=True)

    # 转换为周期数据
    period_df = df.resample(rule=period_type).last()  # 大部分columns，在转换时使用last

    period_df['开盘价'] = df['开盘价'].resample(period_type).first()
    period_df['最高价'] = df['最高价'].resample(period_type).max()
    period_df['最低价'] = df['最低价'].resample(period_type).min()
    period_df['成交额'] = df['成交额'].resample(period_type).sum()
    period_df['涨跌幅'] = df['涨跌幅'].resample(period_type).apply(lambda x: (x + 1.0).prod() - 1.0)

    period_df['每天资金曲线'] = df['涨跌幅'].resample(period_type).apply(lambda x: list((x + 1).cumprod()))
    # print period_df
    # print period_df.iloc[1]['每天资金曲线']
    period_df['最后一天涨跌幅'] = df['涨跌幅'].resample(period_type).last()
    period_df['交易天数'] = df['是否交易'].resample(period_type).sum()
    period_df['市场交易天数'] = df['股票代码'].resample(period_type).size()

    # 去除一天都没有交易的周
    period_df.dropna(subset=['股票代码'], inplace=True)

    # 重新设定index
    period_df.reset_index(inplace=True)
    period_df['交易日期'] = period_df['周期最后交易日']
    del period_df['周期最后交易日']

    return period_df
