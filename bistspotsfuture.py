import os
from datetime import datetime
from DataStore import DataStore
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder

def main():
    # DataStore sınıfından bir örnek oluştur
    datastore = DataStore()

    # Authentication yap, gerekli durumlar için login olmak gerekebilir
    datastore.auth()

    # Bugünün tarihini al
    today = datetime.today().strftime('%Y%m%d')

    # Kontrol edilecek dosyanın ismi
    viopms_file = './EOD/BULTEN/viopms_20250123.csv'

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

    # Yeni sütunları oluştur ve kurallara göre doldur
    filtered_indexes['BIST 30'] = (filtered_indexes['INDICES'] == 'BIST 30').astype(int)
    filtered_indexes['BIST 50'] = ((filtered_indexes['INDICES'] == 'BIST 50') | (filtered_indexes['INDICES'] == 'BIST 30')).astype(int)
    filtered_indexes['BIST 100'] = ((filtered_indexes['INDICES'] == 'BIST 100') | (filtered_indexes['BIST 50'] == 1)).astype(int)

    # Öncelikli sıralama: BIST 30 > BIST 50 > BIST 100
    priority_mapping = {"BIST 30": 1, "BIST 50": 2, "BIST 100": 3}
    filtered_indexes['PRIORITY'] = filtered_indexes['INDICES'].map(priority_mapping)

    # Alfabetik sıralama ve öncelik sırasına göre sıralama
    filtered_indexes = filtered_indexes.sort_values(by=['EQUITY CODE', 'PRIORITY']).drop_duplicates(subset=['EQUITY CODE'], keep='first')

    # EQUITY CODE ve INDICES sütunlarını seç
    filtered_data = filtered_indexes[['EQUITY CODE', 'INDICES', 'BIST 30', 'BIST 50', 'BIST 100']]

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
        print("VIOPMS tablosu bulunamadı, işlem gerçekleştirilemiyor.", viopms_file)
        return

    # SOZLESME KODU'nu eklemek için genişletilmiş veri setini oluştur
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
                    'SOZLESME KODU': sozlesme_kodu,
                    'BIST 30': row['BIST 30'],
                    'BIST 50': row['BIST 50'],
                    'BIST 100': row['BIST 100']
                })

    # Yeni verileri DataFrame'e dönüştür
    expanded_df = pd.DataFrame(expanded_data)

    # Streamlit arayüzü için filtre seçeneklerini ekle
    st.title("Filtered Data")

    col1, col2 = st.columns(2)

    with col1:
        positive_filter = st.selectbox("Pozitif Filtre", ["Hepsi", "BIST 100", "BIST 50", "BIST 30"])

    with col2:
        negative_filter = st.selectbox("Negatif Filtre", ["Hepsi", "BIST 100", "BIST 50", "BIST 30"])

    # Pozitif filtreyi uygula
    if positive_filter == "BIST 100":
        expanded_df = expanded_df[expanded_df['BIST 100'] == 1]
    elif positive_filter == "BIST 50":
        expanded_df = expanded_df[expanded_df['BIST 50'] == 1]
    elif positive_filter == "BIST 30":
        expanded_df = expanded_df[expanded_df['BIST 30'] == 1]

    # Negatif filtreyi uygula
    if negative_filter == "BIST 100":
        expanded_df = expanded_df[expanded_df['BIST 100'] == 0]
    elif negative_filter == "BIST 50":
        expanded_df = expanded_df[expanded_df['BIST 50'] == 0]
    elif negative_filter == "BIST 30":
        expanded_df = expanded_df[expanded_df['BIST 30'] == 0]

    # Filtrelenmiş veriyi CSV dosyasına kaydet
    expanded_df.to_csv("filtered.csv", index=False)

    # Filtrelenmiş veriyi AgGrid kullanarak görüntüle (sayfa boyutuna göre ayarla)
    if not expanded_df.empty:
        gb = GridOptionsBuilder.from_dataframe(expanded_df)
        gb.configure_default_column(editable=True, groupable=True, filter=True)
        gb.configure_grid_options(domLayout='autoHeight')  # Sayfa boyutuna göre ayarlandı
        grid_options = gb.build()
        AgGrid(expanded_df, gridOptions=grid_options, fit_columns_on_grid_load=True)  # Fit sütunları etkinleştir
    else:
        st.write("Hiçbir veri bulunamadı.")

if __name__ == "__main__":
    main()