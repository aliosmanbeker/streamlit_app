import streamlit as st
import pandas as pd
import os
from DataStore import DataStore
from st_aggrid import AgGrid, GridOptionsBuilder

def show_page():
    st.title("BRUT TAKAS Verileri")

    # DataStore sınıfından bir örnek oluştur
    datastore = DataStore()
    datastore.auth()

    # Bir önceki iş gününün tarihini hesapla
    previous_business_day = datastore.date.strftime('%Y%m%d')

    # İndirilen dosyanın adını kontrol et
    thb_folder = './EOD/BULTEN/'  # THB dosyalarının bulunduğu klasör
    thb_file_name = f'thb{previous_business_day}1.csv'
    thb_file_path = os.path.join(thb_folder, thb_file_name)

    # THB dosyasını kontrol et
    if not os.path.exists(thb_file_path):
        try:
            datastore.download_eqty_table()
        except Exception as e:
            st.error(f"THB dosyası indirilirken bir hata oluştu: {str(e)}")
            return


    # BRUT TAKAS sütununda 1 olan verileri kontrol et ve göster
    try:
        thb_data = pd.read_csv(thb_file_path, delimiter=';', encoding='utf-8')
        thb_data.columns = thb_data.columns.str.strip()  # Sütun isimlerini temizle

        # BRUT TAKAS sütununda 1 olan verileri filtrele
        brut_takas_filtered = thb_data[thb_data['BRUT TAKAS'] == "1"]

        # ISLEM KODU sütununu seç
        islem_kodu_data = brut_takas_filtered[['ISLEM  KODU']]

        # Sonuçları ekrana yazdır ve CSV dosyasına kaydet
        if islem_kodu_data.empty:
            st.warning("BRUT TAKAS sütununda 1 olan veri bulunamadı.")
        else:
            output_file_path = os.path.join(thb_folder, f'brut_takas_{previous_business_day}.csv')
            islem_kodu_data.to_csv(output_file_path, index=False, encoding='utf-8')
            st.write("BRUT TAKAS var olan hisseler:")

            # Grid yapılandırması (senin istediğin şekilde)
            gb = GridOptionsBuilder.from_dataframe(islem_kodu_data)
            gb.configure_default_column(editable=True, groupable=True, filter=True)  # Özelleştirilmiş ayarlar
            grid_options = gb.build()

            # AgGrid ile tabloyu göster
            AgGrid(
                islem_kodu_data,
                gridOptions=grid_options,
                height=500,  # Tablo yüksekliği
                fit_columns_on_grid_load=True  # Sütunların tabloya otomatik sığdırılması
            )
    except KeyError as e:
        st.error(f"Gerekli sütun eksik: {e}")
    except Exception as e:
        st.error(f"THB dosyası işlenirken bir hata oluştu: {str(e)}")