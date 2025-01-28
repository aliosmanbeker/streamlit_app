import streamlit as st
import numpy as np
import pandas as pd
import os
from st_aggrid import AgGrid, GridOptionsBuilder
from DataStore import DataStore

def main():

    st.title("Hisse Açıklık Tablosu")
    st.text("Piyasa değeri bir önceki kapanış fiyatına göre hesaplamaktadır!")

    # DataStore sınıfından bir örnek oluştur
    datastore = DataStore()

    # Tarih kontrolü için bugünden bir önceki iş gününün tarihi
    previous_business_day = datastore.date.strftime('%Y%m%d')

    # İndirilen dosyaların isimleri
    eqty_file_path = f"./EOD/BULTEN/thb{previous_business_day}1.csv"
    indexes_file_path = "./EOD/BULTEN/endeks_tablosu.csv"
    endeks_agirlik_path = "./EOD/BULTEN/endeks_agirlik.csv"

    # Dosyaların kontrolü
    eqty_exists = os.path.exists(eqty_file_path)
    indexes_exists = os.path.exists(indexes_file_path)

    if not (eqty_exists and indexes_exists):
        st.write("Dosyalar eksik veya tarih uyumsuz. Yeniden indiriliyor...")
        try:
            # Authentication işlemi
            datastore.auth()

            # Hisse senedi tablosunu indir ve kaydet
            st.write("Hisse Senedi Tablosu indiriliyor...")
            datastore.download_eqty_table()
            st.write("Hisse Senedi Tablosu başarıyla indirildi.")

            # Endeks tablosunu indir ve kaydet
            st.write("Endeks Tablosu indiriliyor...")
            indexes = datastore.get_indexes()
            indexes.to_csv(indexes_file_path, index=False)
            st.write("Endeks Tablosu başarıyla indirildi ve 'endeks_tablosu.csv' dosyasına kaydedildi.")
        except Exception as e:
            st.error(f"Veriler indirilirken bir hata oluştu: {e}")
            return

    try:
        indexes_df = pd.read_csv(indexes_file_path)

        required_columns = ['EQUITY CODE', ' EQUITY NAME', 'TOTAL NUMBER OF SHARES', 'FREE FLOAT RATIO']
        missing_columns = [col for col in required_columns if col not in indexes_df.columns]

        if missing_columns:
            st.error(f"Eksik sütunlar: {', '.join(missing_columns)}")
            return

        xu100_filtered = indexes_df[indexes_df['INDEX CODE'] == 'XU100']
        equity_codes = xu100_filtered[['EQUITY CODE', ' EQUITY NAME', 'TOTAL NUMBER OF SHARES', 'FREE FLOAT RATIO']].copy()

        # Halka Açık Senet sütununu hesaplayıp ekle
        equity_codes['TOTAL NUMBER OF SHARES'] = pd.to_numeric(equity_codes['TOTAL NUMBER OF SHARES'], errors='coerce')
        equity_codes['FREE FLOAT RATIO'] = pd.to_numeric(equity_codes['FREE FLOAT RATIO'], errors='coerce')
        equity_codes['HALKA ACIK SENET'] = equity_codes['TOTAL NUMBER OF SHARES'] * equity_codes['FREE FLOAT RATIO']

        # Hisse senedi tablosunu oku
        eqty_df = pd.read_csv(eqty_file_path, delimiter=';')
        eqty_df['KAPANIS FIYATI'] = pd.to_numeric(eqty_df['KAPANIS FIYATI'], errors='coerce')

        # Halka Açık Değer sütununu hesaplayıp ekle
        equity_codes = equity_codes.merge(
            eqty_df[['ISLEM  KODU', 'KAPANIS FIYATI']],
            left_on='EQUITY CODE',
            right_on='ISLEM  KODU',
            how='left'
        )
        equity_codes['HALKA ACIK DEGER'] = equity_codes['HALKA ACIK SENET'] * equity_codes['KAPANIS FIYATI']

        # Piyasa Değeri sütununu hesaplayıp ekle
        equity_codes['PIYASA DEGERI'] = equity_codes['TOTAL NUMBER OF SHARES'] * equity_codes['KAPANIS FIYATI']

        # Halka Açık Değer, Halka Açık Senet, Kapanış Fiyatı ve Piyasa Değeri sütunlarındaki değerleri yuvarla
        equity_codes['TOPLAM PAY SAYISI'] = np.round(equity_codes['TOTAL NUMBER OF SHARES'])
        equity_codes['HALKA ACIK SENET'] = np.round(equity_codes['HALKA ACIK SENET'])
        equity_codes['HALKA ACIK DEGER'] = np.round(equity_codes['HALKA ACIK DEGER'])
        equity_codes['PIYASA DEGERI'] = np.round(equity_codes['PIYASA DEGERI'])

        # Sadece gerekli sütunları kaydet
        final_data = equity_codes[['EQUITY CODE', ' EQUITY NAME', 'TOPLAM PAY SAYISI', 'FREE FLOAT RATIO', 'HALKA ACIK SENET', 'HALKA ACIK DEGER', 'PIYASA DEGERI']]
        # Son kullanıcıya gösterilecek sütun isimlerini değiştir
        final_data = final_data.rename(columns={
            'EQUITY CODE': 'HISSE KODU',
            ' EQUITY NAME': 'HISSE ADI',
            'FREE FLOAT RATIO': 'DOLAŞIMDAKİ PAY ORANI'
        })

        # Streamlit ile tabloyu AgGrid'de göster
        st.subheader("Endeks Ağırlık Tablosu")
        gb = GridOptionsBuilder.from_dataframe(final_data)

        # Sayısal sütunları binlik ayracı ile göstermek için formatlama
        numeric_columns = ['TOPLAM PAY SAYISI', 'HALKA ACIK SENET', 'HALKA ACIK DEGER', 'PIYASA DEGERI']
        for col in numeric_columns:
            gb.configure_column(col, type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
                                valueFormatter="x.toLocaleString('en-US')")  # Binlik ayracı formatı

        gb.configure_default_column(editable=True, groupable=True, filter=True)
        grid_options = gb.build()
        AgGrid(final_data, gridOptions=grid_options, height=500, fit_columns_on_grid_load=True)

        # İndirilebilir bağlantı
        st.download_button(
            label="Endeks Ağırlık Tablosunu İndir",
            data=final_data.to_csv(index=False),
            file_name="endeks_agirlik.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"XU100 Endeks Ağırlık Tablosu oluşturulurken bir hata oluştu: {e}")

if __name__ == "__main__":
    main()
