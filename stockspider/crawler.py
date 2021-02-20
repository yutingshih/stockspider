#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Some useful functions used to crawl TWSE data

import os, io, time, sqlite3
from datetime import date, timedelta
import requests as req
import pandas as pd
from typing import Union, List
NumType = Union[int, str]


def getDailyPrice(day: str = 'yesterday') -> pd.DataFrame:
    ''' Get daily price from www.twse.com.tw and return a DataFrame '''

    if day == 'yesterday':
        day = (date.today() - timedelta(days=1)).strftime('%Y%m%d')
    elif day == 'today':
        day = date.today().strftime('%Y%m%d')
    
    res = req.get(f'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=html&date={day}&type=ALLBUT0999')
    res.encoding = 'utf-8'

    try:
        df = pd.read_html(res.text)[-1]
    except:
        return None
    
    if type(df.columns) == pd.MultiIndex:
        df.columns = [col[-1] for col in df.columns]
    
    df['date'] = pd.to_datetime(day)
    df['date'] = df['date'].dt.date
    df.rename(columns={'證券代號': 'stockID'}, inplace=True)
    df.set_index(['stockID', 'date'], inplace=True)
    
    df = df.apply(lambda row: pd.to_numeric(row, errors='coerce'))
    df.dropna(axis=1, how='all', inplace=True)

    return df


def getMonthlyReport(year: int, month: int) -> pd.DataFrame:
    ''' Get monthly report from mops.twse.com.tw and return a DataFrame '''

    year %= 1911
    form_data = {
        'step': 9,
        'unctionName': 'show_file',
        'filePath': '/home/html/nas/t21/sii/',
        'fileName': f't21sc03_{year}_{month}.csv'
    }
    res = req.post('https://mops.twse.com.tw/server-java/FileDownLoad', data=form_data)
    res.encoding = 'utf-8'
    df = pd.read_csv(io.StringIO(res.text))

    df.set_index(['公司代號', '公司名稱'], inplace=True)

    for col in df.columns:
        df.rename(columns={col: col.split('-')[-1]}, inplace=True)

    df = df.apply(lambda row: pd.to_numeric(row, errors='coerce'))
    df.dropna(axis=1, how='all', inplace=True)

    return df


def getFinancialReport(stockID: NumType, year: NumType, season: NumType) -> List[pd.DataFrame]:
    year %= 1911
    form_data = parseFormData(f'step=1&DEBUG=&CO_ID={stockID}&SYEAR={year}&SSEASON={season}&REPORT_ID=C')

    res = req.post('https://mops.twse.com.tw/server-java/t164sb01', data=form_data)
    res.encoding = 'big5'
    return pd.read_html(res.text)


def saveDataCSV(data: pd.DataFrame, filename: str, overwrite: bool = True) -> bool:
    ''' save a DataFrame as csv file and return wheather it is successfully saved '''
    
    if type(data) != pd.DataFrame:
        return False
    
    filename = os.path.splitext(filename)[0] + '.csv'
    if overwrite or not os.path.exists(filename):
        data.to_csv(filename, encoding='utf-8-sig')
    return True


def saveDataSQL(data: pd.DataFrame, filename: str, tablename: str, if_exists: str = 'replace') -> bool:
    ''' save a DataFrame as csv file and return wheather it is successfully saved '''

    if type(data) != pd.DataFrame:
        return False

    filename = os.path.splitext(filename)[0] + '.db'
    con = sqlite3.connect(filename)
    data.to_sql(tablename, con, if_exists=if_exists)
    con.close()
    return True


def loadDataSQL(fileName: str, tablename: str) -> pd.DataFrame:
    ''' load the table from the database file and return a DataFrame '''

    con = sqlite3.connect(fileName)
    return pd.read_sql(f'SELECT * FROM {tablename}', con, index_col=['stockID'], parse_dates=['date'])
    con.close()


def parseFormData(src: str) -> dict:
    return dict([prm.split('=') for prm in src.split('&')])


def getManyDays(path, num_days, day=date.today()):
    while num_days:
        print(f'{day} ', end='')
        df = getDailyPrice(day.strftime('%Y%m%d'))
        if saveDataSQL(df, path, 'daily_price', 'append'):
            num_days -= 1
            print(f'downloaded')
        else:
            print(f'skipped')
        day -= timedelta(days=1)
        time.sleep(1)
    print(f'done')
    return df


if __name__ == '__main__':
    pass
