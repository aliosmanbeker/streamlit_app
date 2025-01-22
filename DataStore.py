import json
import requests
import holidays
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
from datetime import datetime, timedelta
from pandas.tseries.offsets import CustomBusinessDay
import pandas as pd
import configparser
import ast
import os
import csv


class DataStore():
    def __init__(self):
        self.connected = False
        self.this_year = datetime.today().year
        self.turkey_holidays = holidays.Turkey(years=self.this_year)
        # self.turkey_holidays = holidays.Turkey(years=[2023, 2024, 2025, 2026])  #burada yıl ekleyebilirsiniz
        # olağan dışı borsa kapalı günlerinde test için aşağıya ' - timedelta(days=5)'
        # holidays_list = [{'24-04-2023':'Republic Day India'}, ]

        config = configparser.ConfigParser()
        config.read('config.ini')

        self.email = config['datastore']['email']
        self.password = config['datastore']['password']
        self.extra_holidays = ast.literal_eval(config['datastore']['extra_holidays'])
        self.lookback = int(config['datastore']['lookback'])
        self.turkey_holidays.append(self.extra_holidays)
        self.date = (datetime.today() - CustomBusinessDay(n=1, holidays=self.turkey_holidays)) - timedelta(
            days=int(self.lookback))
        self.datename = self.date.strftime('%Y%m%d')
        # print('date: ' + str(self.date))

    def auth(self):
        login_url = 'https://datastore.borsaistanbul.com/api/login'
        header = {"Content-Type": "application/json"}
        # buradaki login bilgileri değiştirebilir
        body = {
            "email": self.email,
            "password": self.password
        }
        r = requests.post(login_url, headers=header, json=body)
        self.auth_token = r.json()['accessToken']

    def __download(self, url):
        headers = {
            "Content-Type": "application/json",
            "x-auth-token": self.auth_token
        }
        file = requests.get(url, headers=headers)
        return file

    def get_indexes(self, date=True):
        if date:
            date = self.datename
        else:
            date = date.strftime('%Y%m%d')
        indexes_file_name = 'endeks_agirlik_ds_genel_' + date + '.csv'
        indexes_file_url = 'https://download.borsaistanbul.com/api/file?file-name=' + f'{indexes_file_name}' + '&file-date=' + f'{date}'
        # indexes_file_url= "https://download.borsaistanbul.com/api/file?file-name=endeks_agirlik_ds_genel_20231025.csv&file-date=20231025"
        print(indexes_file_url)
        file = DataStore.__download(self, indexes_file_url)
        # print("file",file)
        indexes = pd.read_csv(BytesIO(file.content), delimiter=';', index_col=[0], skiprows=1)
        return indexes

    def get_divisors(self, date='True'):
        if date == 'True':
            date = self.datename
        else:
            date = date.strftime('%Y%m%d')
        divisors_file_name = 'endeks_bolen_ds_genel_' + date + '.csv'
        divisors_file_url = 'https://download.borsaistanbul.com/api/file?file-name=' + f'{divisors_file_name}' + '&file-date=' + f'{date}'
        # divisors_file_url = "https://download.borsaistanbul.com/api/file?file-name=endeks_bolen_ds_genel_20231026.csv&file-date=20231026"
        print(divisors_file_url)
        file = DataStore.__download(self, divisors_file_url)
        # print("file from divisors",file)
        # print(pd.read_csv(BytesIO(file.content)))
        divisors = pd.read_csv(BytesIO(file.content), delimiter=';')
        return divisors

    def get_eqty_table(self, date='True'):
        if date == 'True':
            date = self.date
        url = 'https://borsaistanbul.com/data/thb/'
        url = url+ date.strftime('%Y') + '/' + date.strftime('%m') + '/thb' + date.strftime('%Y%m%d') + '1.zip'
        print(url)
        response = urlopen(url)
        zip_file = ZipFile(BytesIO(response.read()))
        eqtyTable = pd.read_csv(zip_file.open(f'{zip_file.namelist()[0]}'), delimiter=';', skiprows=1)
        # 10-07-2023 güncellenme, türkçe header kaldırıldı, "ISLEM  KODU" yerine "INSTRUMENT SERIES CODE" kullanılmalı
        return eqtyTable

    def download_eqty_table(self, date='True'):
        if date == 'True':
            date = self.date
        url = 'https://borsaistanbul.com/data/thb/'
        response = urlopen(
            url + date.strftime('%Y') + '/' + date.strftime('%m') + '/thb' + date.strftime('%Y%m%d') + '1.zip')
        zip_file = ZipFile(BytesIO(response.read()))
        # eqtyTable = pd.read_csv(zip_file.open(f'{zip_file.namelist()[0]}'), delimiter=';', header=1)
        file = zip_file.namelist()[0]
        path = './EOD/BULTEN'
        zip_file.extract(file, path=path)
        print('downloaded: ', path + '/' + file)
        pass

    def download_viop_table(self, date='True'):
        if date == 'True':
            date = self.date
        url = 'https://borsaistanbul.com/viopdata'
        file_name = '/viop_' + date.strftime('%Y%m%d') + '.csv'
        response = requests.get(
            url + file_name)
        path = './EOD/BULTEN' + file_name
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            for line in response.iter_lines():
                writer.writerow(line.decode('utf-8').split(';'))
        print('downloaded:', path)

    def download_viopms_table(self, date='True'):
        if date == 'True':
            date = self.date
        url = 'https://borsaistanbul.com/viopdata/'
        file_name = '/viopms_' + datetime.today().strftime('%Y%m%d') + '.csv'
        response = requests.get(
            url + file_name)
        print(response)
        path = './EOD/BULTEN' + file_name
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            for line in response.iter_lines():
                writer.writerow(line.decode('utf-8').split(';'))
        print('downloaded:', path)

    # .decode('utf-8')
    def get_instrument(self, date="True"):
        if date == 'True':
            date = self.date
        url = 'https://borsaistanbul.com/viopdata/viop_'
        response = urlopen(
            url + date.strftime('%Y') + '/' + date.strftime('%m') + '/thb' + date.strftime('%Y%m%d') + '.zip')
        zip_file = ZipFile(BytesIO(response.read()))

    def get_indexes_names(self, date="True"):
        if date == 'True':
            date = self.datename
        else:
            date = date.strftime('%Y%m%d')
        indexes = self.get_indexes(date)['INDEX CODE'].drop_duplicates().values.tolist()
        return indexes

    def get_futures_list(self):
        url = "https://borsaistanbul.com/data/vadeli/viop_" + self.date.strftime('%Y%m%d') + ".csv"
        # print(url + self.date.strftime('%Y%m%d') + ".csv")
        # response = urlopen(url + self.date.strftime('%Y%m%d') + ".csv") #20230526
        response = (url + self.date.strftime('%Y%m%d') + ".csv")
        file = requests.get(url=url)
        futures = pd.read_csv(BytesIO(file.content), delimiter=';', header=1)[['INSTRUMENT SERIES', 'UNDERLYING']]
        futures = futures[futures['INSTRUMENT SERIES'].str.startswith('F_')]
        # print(futures['INSTRUMENT SERIES'].str.startswith('F_'))
        return futures


if __name__ == "__main__":
    # DataStore sınıfından bir örnek oluştur
    datastore = DataStore()

    # Authentication yap, gerekli durumlar için login olmak gerekebilir
    datastore.auth()

    # Hisse senedi tablosunu indir ve ekrana yazdır
    eqty_table = datastore.download_eqty_table()
    print("Hisse Senedi Tablosu:")
    print(eqty_table)

    # Viop tablosunu indir ve ekrana yazdır
    viop_table = datastore.download_viopms_table()
    print("Mevcut Sözleşmeler Tablosu:")
    print(viop_table)

    # Endeks tablosunu indir, ekrana yazdır ve kaydet
    indexes = datastore.get_indexes()
    print("Endeks Tablosu:")
    print(indexes)
    indexes.to_csv("./EOD/BULTEN/endeks_tablosu.csv", index=False)
    print("Endeks Tablosu 'endeks_tablosu.csv' dosyasına kaydedildi.")

