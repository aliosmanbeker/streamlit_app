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
    viopms_file = f'./EOD/BULTEN/viopms_{today}.csv'

    # Dosyanın var olup olmadığını kontrol et
    if os.path.exists(viopms_file):
        file_date = viopms_file.split('_')[-1].split('.')[0]

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
    indexes = pd.read_csv(endeks_dosyasi)
    # if os.path.exists(endeks_dosyasi):
    #     indexes = pd.read_csv(endeks_dosyasi)
    #     print("Endeks Tablosu yüklendi.")
    # else:
    #     print("Endeks tablosu bulunamadı, işlem gerçekleştirilemiyor.")
    #     return

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

    # Sıralama ve benzersiz hale getirme
    filtered_indexes = filtered_indexes.sort_values(by=['EQUITY CODE', 'PRIORITY']).drop_duplicates(subset=['EQUITY CODE'], keep='first')

    # Gerekli sütunları seç
    filtered_data = filtered_indexes[['EQUITY CODE', 'INDICES', 'BIST 30', 'BIST 50', 'BIST 100']]
    with open(viopms_file, 'r', encoding='utf-8') as file:
        header = file.readline().strip().split(',')
        viopms_data = pd.read_csv(viopms_file, delimiter=',', skiprows=1, names=header)

    # Benzersiz bir veri seti oluştur
    expanded_data = []
    for _, row in filtered_data.iterrows():
        equity_code = row['EQUITY CODE']
        indices = row['INDICES']

        # DAYANAK VARLIK sütununda eşleşme ara
        matches = viopms_data[viopms_data['DAYANAK VARLIK'] == equity_code]

        # F_ ile başlayan SOZLESME KODU değerlerini birleştir
        sozlesme_kodlari = ", ".join(matches[matches['SOZLESME KODU'].str.startswith('F_')]['SOZLESME KODU'].unique())

        expanded_data.append({
            'EQUITY CODE': equity_code,
            'INDICES': indices,
            'SOZLESME KODU': sozlesme_kodlari,
            'BIST 30': row['BIST 30'],
            'BIST 50': row['BIST 50'],
            'BIST 100': row['BIST 100']
        })

    # Yeni verileri DataFrame'e dönüştür
    expanded_df = pd.DataFrame(expanded_data)

    # Filtreleme ve CSV'ye yazma
    expanded_df.to_csv("filtered.csv", index=False)

    # Streamlit arayüzü
    st.title("Filtered Data")

    col1, col2, col3 = st.columns(3)
    with col1:
        positive_filter = st.selectbox("Pozitif Filtre", ["Hepsi", "BIST 100", "BIST 50", "BIST 30"])
    with col2:
        negative_filter = st.selectbox("Negatif Filtre", ["Hepsi", "BIST 100", "BIST 50", "BIST 30"])
    with col3:
        future_filter = st.radio("Future Filtre", ["Future Olmayanları Çıkart", "Hepsini Göster"], index=0)

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

    # Future olmayanları çıkart filtresi
    if future_filter == "Future Olmayanları Çıkart":
        expanded_df = expanded_df[expanded_df['SOZLESME KODU'] != ""]

    # Filtrelenmiş veriyi CSV dosyasına kaydet
    expanded_df.to_csv("filtered_bist.csv", index=False)

    # AgGrid ile interaktif tablo
    if not expanded_df.empty:
        gb = GridOptionsBuilder.from_dataframe(expanded_df)
        gb.configure_default_column(editable=True, groupable=True, filter=True)
        grid_options = gb.build()
        AgGrid(expanded_df, gridOptions=grid_options, height=500, fit_columns_on_grid_load=True)
    else:
        st.write("Hiçbir veri bulunamadı.")

if __name__ == "__main__":
    main()