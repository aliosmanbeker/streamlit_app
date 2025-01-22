import os
from datetime import datetime
from DataStore import DataStore
import pandas as pd
import streamlit as st

def main():
    # DataStore sınıfından bir örnek oluştur
    datastore = DataStore()

    # Authentication yap, gerekli durumlar için login olmak gerekebilir
    datastore.auth()

    # Bugünün tarihini al
    today = datetime.today().strftime('%Y%m%d')

    # Kontrol edilecek dosyanın ismi
    viopms_file = './EOD/BULTEN/viopms_20250122.csv'

    # Dosyanın var olup olmadığını kontrol et
    if os.path.exists(viopms_file):
        # Dosya adındaki tarihi al
        file_date = viopms_file.split('_')[-1].split('.')[0]

        # Dosya tarihi bugünün tarihiyle eşleşiyorsa indirme işlemi yapılmaz
        if file_date == today:
            print("Dosya güncel. İşlem devam ediyor...")
        else:
            print("Dosya tarihi güncel değil. İndirme işlemi başlatılıyor...")
            datastore.download_eqty_table()
            datastore.download_viopms_table()
            indexes = datastore.get_indexes()
            indexes.to_csv("./EOD/BULTEN/endeks_tablosu.csv", index=False)
    else:
        print("Dosya bulunamadı. İndirme işlemi başlatılıyor...")
        datastore.download_eqty_table()
        datastore.download_viopms_table()
        indexes = datastore.get_indexes()
        indexes.to_csv("./EOD/BULTEN/endeks_tablosu.csv", index=False)

    # Endeks Tablosu'nu yükle
    endeks_dosyasi = "./EOD/BULTEN/endeks_tablosu.csv"
    if os.path.exists(endeks_dosyasi):
        indexes = pd.read_csv(endeks_dosyasi)
        print("Endeks Tablosu yüklendi.")
    else:
        print("Endeks tablosu bulunamadı, işlem gerçekleştirilemiyor.")
        return

    # Endeks Tablosu'ndan sonu .E ile biten EQUITY CODE değerlerini filtrele
    filtered_indexes = indexes[indexes['EQUITY CODE'].str.endswith('.E', na=False)]

    # Sadece belirli INDICES değerlerini içerenleri filtrele
    valid_indices = ["BIST 100", "BIST 50", "BIST 30"]
    filtered_indexes = filtered_indexes[filtered_indexes['INDICES'].isin(valid_indices)]

    # Öncelikli sıralama: BIST 30 > BIST 50 > BIST 100
    priority_mapping = {"BIST 30": 1, "BIST 50": 2, "BIST 100": 3}
    filtered_indexes['PRIORITY'] = filtered_indexes['INDICES'].map(priority_mapping)

    # Alfabetik sıralama ve öncelik sırasına göre sıralama
    filtered_indexes = filtered_indexes.sort_values(by=['EQUITY CODE', 'PRIORITY']).drop_duplicates(subset=['EQUITY CODE'], keep='first')

    # EQUITY CODE ve INDICES sütunlarını seç
    filtered_data = filtered_indexes[['EQUITY CODE', 'INDICES']]

    # VIOPMS dosyasını yükle
    if os.path.exists(viopms_file):
        with open(viopms_file, 'r', encoding='utf-8') as file:
            header = file.readline().strip().split(',')
            if 'DAYANAK VARLIK' in header and 'SOZLESME KODU' in header:
                viopms_data = pd.read_csv(viopms_file, delimiter=',', skiprows=1, names=header)
                print("VIOPMS Tablosu başarıyla yüklendi.")
            else:
                print("Gerekli sütunlar bulunamadı: DAYANAK VARLIK veya SOZLESME KODU eksik.")
                return
    else:
        print("VIOPMS tablosu bulunamadı, işlem gerçekleştirilemiyor.")
        return

    # FILTERED dosyasına yeni sütun ekle
    expanded_data = []

    for _, row in filtered_data.iterrows():
        equity_code = row['EQUITY CODE']
        indices = row['INDICES']

        # DAYANAK VARLIK sütununda eşleşme ara
        matches = viopms_data[viopms_data['DAYANAK VARLIK'] == equity_code]

        # SOZLESME KODU sütunundan F_ ile başlayanları al
        for _, match_row in matches.iterrows():
            sozlesme_kodu = match_row['SOZLESME KODU']
            if sozlesme_kodu.startswith('F_'):
                expanded_data.append({
                    'EQUITY CODE': equity_code,
                    'INDICES': indices,
                    'SOZLESME KODU': sozlesme_kodu
                })

    # Yeni verileri DataFrame'e dönüştür
    expanded_df = pd.DataFrame(expanded_data)

    # Streamlit sayfasında görüntüle
    st.title("Filtered Data")
    if not expanded_df.empty:
        st.dataframe(expanded_df)
    else:
        st.write("Hiçbir veri bulunamadı.")

if __name__ == "__main__":
    main()