import streamlit as st
import os
import pandas as pd
from datetime import datetime
from DataStore import DataStore

# Streamlit sayfasını tanımlayın
def main():
    st.title("VIOP ve Hisse Senedi Verileri")

    # DataStore sınıfından bir örnek oluştur
    datastore = DataStore()

    # Authentication yap, API erişimi için giriş işlemi
    st.write("Oturum açılıyor...")
    datastore.auth()

    def check_file_date(file_name):
        """
        Dosya adındaki tarihin bugünün tarihi ile eşleşip eşleşmediğini kontrol eder.
        """
        try:
            file_date_str = file_name.split('_')[-1].split('.')[0]  # Tarih kısmını ayıkla
            file_date = datetime.strptime(file_date_str, '%Y%m%d').date()
            today = datetime.today().date()
            return file_date == today
        except Exception as e:
            st.write(f"Tarih kontrolü sırasında hata oluştu: {e}")
            return False

    def download_eqty_and_viop_tables():
        eqty_path = './EOD/BULTEN'
        viop_path = './EOD/BULTEN'

        os.makedirs(eqty_path, exist_ok=True)  # Klasör yoksa oluştur
        os.makedirs(viop_path, exist_ok=True)  # Klasör yoksa oluştur

        eqty_files = [f for f in os.listdir(eqty_path) if f.startswith('thb') and f.endswith('.zip')]
        viop_files = [f for f in os.listdir(viop_path) if f.startswith('viopms') and f.endswith('.csv')]

        if viop_files and check_file_date(viop_files[0]):
            st.write("VIOPMS dosyası bugünün tarihi ile eşleşiyor. Hiçbir dosya indirilmedi.")
            return

        st.write("VIOPMS dosyası güncel değil, dosyalar indiriliyor...")
        datastore.download_viopms_table()  # VIOP dosyasını indir
        datastore.download_eqty_table()  # Hisse senedi dosyasını indir
        st.write("VIOP ve Hisse Senedi tabloları başarıyla indirildi.")

    def process_thb_file():
        st.write("THB dosyası işleniyor...")
        thb_path = './EOD/BULTEN'
        viop_path = './EOD/BULTEN'

        thb_files = [f for f in os.listdir(thb_path) if f.startswith('thb') and f.endswith('.csv')]
        viop_files = [f for f in os.listdir(viop_path) if f.startswith('viopms') and f.endswith('.csv')]

        if not thb_files:
            st.write("THB dosyası bulunamadı!")
            return

        if not viop_files:
            st.write("VIOPMS dosyası bulunamadı!")
            return

        thb_file = os.path.join(thb_path, thb_files[0])  # İlk bulunan THB dosyasını seç
        viop_file = os.path.join(viop_path, viop_files[0])  # İlk bulunan VIOPMS dosyasını seç

        # THB ve VIOPMS dosyalarını yükle
        thb_data = pd.read_csv(thb_file, delimiter=';', encoding='utf-8')
        viop_data = pd.read_csv(viop_file, delimiter=',', encoding='utf-8')  # ',' olarak değiştirdik

        # Sütun isimlerini temizle
        viop_data.columns = viop_data.columns.str.strip()

        # .E ile biten ISLEM KODU değerlerini filtrele
        filtered_data = thb_data[thb_data['ISLEM  KODU'].str.endswith('.E', na=False)]

        # İlgili sütunları seç
        selected_columns = filtered_data[['ISLEM  KODU', 'BIST 100 ENDEKS', 'BIST 30 ENDEKS']]

        # Gerekli sütunları kontrol et
        if 'DAYANAK VARLIK' not in viop_data.columns or 'SOZLESME KODU' not in viop_data.columns:
            st.write("Gerekli sütunlar bulunamadı! Lütfen VIOPMS dosyasını kontrol edin.")
            return

        # Sadece F_ ile başlayan SOZLESME KODU değerlerini filtrele
        viop_data = viop_data[viop_data['SOZLESME KODU'].str.startswith('F_', na=False)]

        # ISLEM KODU'nu VIOPMS dosyasındaki DAYANAK VARLIK sütununda ara
        result_data = []
        for _, row in selected_columns.iterrows():
            matches = viop_data[viop_data['DAYANAK VARLIK'] == row['ISLEM  KODU']]
            for _, match in matches.iterrows():
                result_data.append({
                    'ISLEM  KODU': row['ISLEM  KODU'],
                    'SOZLESME KODU': match['SOZLESME KODU'],
                    'BIST 100 ENDEKS': row['BIST 100 ENDEKS'],
                    'BIST 30 ENDEKS': row['BIST 30 ENDEKS']
                })

        # Sonuçları DataFrame'e dönüştür ve CSV'ye kaydet
        output_data = pd.DataFrame(result_data)
        output_file = './EOD/BULTEN/filtered_thb.csv'
        output_data.to_csv(output_file, index=False, encoding='utf-8')
        st.write(f"Filtrelenmiş ve eşleştirilmiş veriler {output_file} dosyasına kaydedildi.")

        # CSV dosyasını sayfada görüntüle
        st.write("**Filtered THB Verileri**")
        st.dataframe(output_data)

    # Hisse senedi ve VIOP tablolarını indirme işlemi
    download_eqty_and_viop_tables()

    # THB dosyasını işle
    process_thb_file()

    st.write("Tüm işlemler başarıyla tamamlandı!")

if __name__ == "__main__":
    main()