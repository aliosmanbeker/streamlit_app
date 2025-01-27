import streamlit as st
import os
import pandas as pd
from datetime import datetime
from DataStore import DataStore
from st_aggrid import AgGrid, GridOptionsBuilder

def show_page():
    st.title("Brüt Takas Hisseleri")
    st.write("Bu sayfa, Brüt Takas Hisselerini listelemek ve ilgili işlemleri gerçekleştirmek için tasarlanmıştır.")

    # DataStore sınıfından bir örnek oluştur
    datastore = DataStore()

    # Tarih kontrolü için bugünden bir önceki iş gününün tarihi
    previous_business_day = datastore.date.strftime('%Y%m%d')

    # İndirilecek dosyanın tam yolu
    file_name = f'thb{previous_business_day}1.csv'
    file_path = f'./EOD/BULTEN/{file_name}'
    csv_output_path = './EOD/BULTEN/brut_takas.csv'

    # Dosyanın mevcut olup olmadığını kontrol et
    eqty_exists = os.path.exists(file_path)

    if not eqty_exists:
        st.write("THB dosyası eksik veya tarih uyumsuz. Yeniden indiriliyor...")
        try:
            # Authentication işlemi
            datastore.auth()

            # Hisse senedi tablosunu indir ve kaydet
            st.write("Hisse Senedi Tablosu indiriliyor...")
            datastore.download_eqty_table()
            st.write(f"Hisse Senedi Tablosu başarıyla indirildi: {file_path}")
        except Exception as e:
            st.error(f"THB dosyası indirilirken bir hata oluştu: {e}")
            return

    # PAZAR sütunu için mapping
    market_mapping = {
        "Z": "YILDIZ PAZAR",
        "N": "ANA PAZAR",
        "T": "ALT PAZAR",
        "W": "YİP",
        "K": "YÜFP",
        "Q": "GSP",
        "E": "EMTİA PAZARI",
        "S": "PÖİP"
    }

    # Dosyayı oku
    eqty_table = pd.read_csv(file_path, delimiter=';', dtype=str)

    # BRUT TAKAS sütunu 1 olan satırları filtrele ve sütunları seç
    filtered_data = eqty_table[eqty_table['BRUT TAKAS'] == '1'][['ISLEM  KODU', 'BULTEN ADI', 'BRUT TAKAS', 'PAZAR']]

    # PAZAR sütununu mapping ile dönüştür
    filtered_data['PAZAR'] = filtered_data['PAZAR'].map(market_mapping)

    # Tabloya SIRA sütununu 1'den başlayarak ekle
    filtered_data.reset_index(drop=True, inplace=True)
    filtered_data.insert(0, 'SIRA', range(1, len(filtered_data) + 1))

    # Filtrelenmiş veriyi kaydet
    filtered_data.to_csv(csv_output_path, index=False, encoding='utf-8-sig')

    show_aggrid(filtered_data)

def show_aggrid(dataframe):
    """Ag-Grid kullanarak DataFrame'i Streamlit'te göster."""
    gb = GridOptionsBuilder.from_dataframe(dataframe)

    # Varsayılan sütun ayarları
    gb.configure_default_column(editable=True, groupable=True, filter=True)

    # Grid yapılandırmasını oluştur
    grid_options = gb.build()

    AgGrid(
        dataframe,
        gridOptions=grid_options,
        height=500,
        fit_columns_on_grid_load=True
    )
