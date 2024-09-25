import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from st_copy_to_clipboard import st_copy_to_clipboard

# Dosya adları
viopms_file = 'EOD/BULTEN/viopms_20240924.csv'
thb_file = 'EOD/BULTEN/thb202409231.csv'
matched_data_file = 'matched_data.csv'

# Matched Data'nın ne zaman oluşturulduğunu kontrol et
def is_data_outdated(file_path):
    if not os.path.exists(file_path):
        return True
    file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
    return datetime.now() - file_mod_time > timedelta(days=1)

# Ana sayfa için fonksiyon
def show_page():
    # Verileri matched_data.csv'den okuma veya yeniden oluşturma
    if is_data_outdated(matched_data_file):
        # Dosyaları okuma
        viopms_df = pd.read_csv(viopms_file, delimiter=',')
        viopms_df.columns = viopms_df.columns.str.strip()  # Sütun adlarını temizle

        # viopms dosyasından DAYANAK VARLIK sütununu alıp sonundaki '.E' kısmını çıkar
        viopms_df['DAYANAK VARLIK'] = viopms_df['DAYANAK VARLIK'].str.replace('.E', '', regex=False)

        # thb dosyasını doğru şekilde okuma
        thb_df = pd.read_csv(thb_file, delimiter=';')
        thb_df.columns = thb_df.columns.str.strip()  # Sütun adlarını temizle

        # Eşleşen veriler için boş bir liste
        matching_data = []

        # Her bir DAYANAK VARLIK için, thb dosyasındaki BULTEN ADI sütununda arama yap
        for index, row in viopms_df.iterrows():
            underlying_asset = row['DAYANAK VARLIK']

            # Eğer underlying_asset NaN ise veya string değilse işlemi atla
            if pd.isna(underlying_asset) or not isinstance(underlying_asset, str):
                continue

            # "BULTEN ADI" sütununda arama yap
            matched_rows = thb_df[thb_df['BULTEN ADI'].str.contains(underlying_asset, na=False)]

            if not matched_rows.empty:
                for _, matched_row in matched_rows.iterrows():
                    # SOZLESME KODU "F_" ile başlıyorsa ekle
                    if row['SOZLESME KODU'].startswith("F_"):
                        matching_data.append({
                            'ISLEM KODU': matched_row['ISLEM  KODU'],
                            'BULTEN ADI': matched_row['BULTEN ADI'],
                            'DAYANAK VARLIK': underlying_asset,  # DAYANAK VARLIK sütunu
                            'SOZLESME KODU': row['SOZLESME KODU'],  # SOZLESME KODU "F_" ile başlayanlar
                            'VADE TARIHI': row['VADE TARIHI'],  # VADE TARIHI sütunu
                            'SOZLESME TIPI': row['SOZLESME TIPI'],  # SOZLESME TIPI sütunu
                            'ENSTRUMAN GRUBU': matched_row['ENSTRUMAN GRUBU']  # ENSTRUMAN GRUBU sütunu
                        })

        # Elde edilen verileri bir DataFrame'e dönüştürme
        matching_df = pd.DataFrame(matching_data)

        # Eşleşen verileri yeni bir CSV dosyasına kaydetme
        matching_df.to_csv(matched_data_file, index=False)
        st.write("Veriler yenilendi ve matched_data.csv dosyasına kaydedildi.")
    else:
        # matched_data.csv dosyasından verileri okuma
        matching_df = pd.read_csv(matched_data_file)
        st.write("Veriler matched_data.csv dosyasından yüklendi.")

    # --- Streamlit Filtreleme Seçenekleri ---
    # Dayanak Varlık Filtreleme
    dayanak_varlik = st.text_input("Dayanak Varlık Giriniz (örn: AKBNK):")
    if dayanak_varlik:
        matching_df = matching_df[matching_df['DAYANAK VARLIK'].str.contains(dayanak_varlik, case=False)]

    # ENSTRUMAN GRUBU Filtreleme
    enstruman_grubu = st.text_input("Enstruman Grubu Giriniz (P: EPW, C: ECW):")
    if enstruman_grubu == 'P':
        matching_df = matching_df[matching_df['ENSTRUMAN GRUBU'] == 'EPW']
    elif enstruman_grubu == 'C':
        matching_df = matching_df[matching_df['ENSTRUMAN GRUBU'] == 'ECW']

    # VADE TARIHI Filtreleme
    vade_tarihi = st.selectbox("Vade Tarihi Seçiniz", ["2024-09-30", "2024-10-31", "2024-11-29"])
    if vade_tarihi:
        matching_df = matching_df[matching_df['VADE TARIHI'] == vade_tarihi]

    # Listeyi Oluştur butonu
    if st.button("Listeyi Oluştur"):
        islem_kodu_listesi = matching_df['ISLEM KODU'].tolist()
        string_of_list = str(islem_kodu_listesi).replace("'", "").replace("[", "").replace("]", "")  # Listeyi temizle ve virgülle ayır

        # Kopyalanabilir bir metin alanı göster
        st.text("Warrant Listesi: " + string_of_list)
        st.text("Kopyalamak için aşağıdaki butona tıklayınız")

        # Kopyala butonu (st_copy_to_clipboard kullanarak)
        st_copy_to_clipboard(string_of_list)

    # Filtrelenmiş verileri göster
    st.dataframe(matching_df)
