#!/usr/bin/env python3

# Some useful functions used to crawl TWSE data

import os, io, sqlite3
from datetime import datetime, timedelta
import requests as req
import pandas as pd


def getDailyPrice(date: str = 'yesterday') -> pd.DataFrame:
    ''' Get daily price from www.twse.com.tw and return a DataFrame '''

    if date == 'yesterday':
        date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    elif date == 'today':
        date = datetime.now().strftime('%Y%m%d')
    
    res = req.get(f'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=html&date={date}&type=ALLBUT0999')
    res.encoding = 'utf-8'

    try:
        df = pd.read_html(res.text)[-1]
    except:
        return None
    
    if type(df.columns) == pd.MultiIndex:
        df.columns = [col[-1] for col in df.columns]
    
    df['date'] = pd.to_datetime(date)
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


def saveDataCSV(data: pd.DataFrame, filename: str, overwrite: bool = True) -> bool:
    ''' save a DataFrame as csv file and return wheather it is successfully saved '''
    
    if type(data) != pd.DataFrame:
        return False
    
    filename = os.path.splitext(filename)[0] + '.csv'
    if overwrite or not os.path.exists(filename):
        data.to_csv(filename, encoding='utf-8-sig')
    return True


def saveDataSQL(data: pd.DataFrame, filename: str, tablename: str, if_exists: str = 'replace'):
    ''' save a DataFrame as csv file and return wheather it is successfully saved '''

    if type(data) != pd.DataFrame:
        return False

    filename = os.path.splitext(filename)[0] + '.db'
    con = sqlite3.connect(filename)
    data.to_sql(tablename, con, if_exists=if_exists)
    con.close()
    return True


def loadDataSQL(fileName: str, tablename: str):
    ''' load the table from the database file and return a DataFrame '''

    con = sqlite3.connect(fileName)
    return pd.read_sql(f'SELECT * FROM {tablename}', con, index_col=['stockID'])
    con.close()


if __name__ == '__main__':
    pass