import streamlit as st
import pandas as pd
import re
import os
from datetime import datetime, timedelta
from st_copy_to_clipboard import st_copy_to_clipboard
import holidays
from DataStore import DataStore  # DataStore sınıfını içe aktarıyoruz

# Türkiye resmi tatil günlerini almak için
turkey_holidays = holidays.Turkey()

# Geçerli iş günü hesaplama fonksiyonu
def get_previous_business_day():
    previous_date = datetime.today() - timedelta(days=1)  # Başlangıçta bir gün geri git
    while previous_date.weekday() > 4 or previous_date in turkey_holidays:  # Cumartesi, pazar veya tatil kontrolü
        previous_date -= timedelta(days=1)
    return previous_date.strftime('%Y%m%d')

# Dosya adlarını ve tarih bilgilerini kontrol eden fonksiyon
def check_and_download_thb():
    # Önceki iş gününü al
    previous_business_day = get_previous_business_day()
    thb_filename = f'EOD/BULTEN/thb{previous_business_day}1.csv'

    # Eğer dosya mevcut değilse veya tarihi bir önceki iş gününe ait değilse yeni dosya indir
    if not os.path.exists(thb_filename):
        datastore = DataStore()
        datastore.auth()
        datastore.download_eqty_table()

        # İndirilen dosya ismini bulma
        downloaded_files = os.listdir('EOD/BULTEN')
        downloaded_file = [f for f in downloaded_files if f.startswith("thb") and f.endswith(".csv")]

        # Dosya adını ekrana yazdırma
        if downloaded_file:
            print(f"Indirilen dosya: {downloaded_file[0]}")
        else:
            print("İndirilen dosya bulunamadı. DataStore indirirken bir hata olmuş olabilir.")

    return thb_filename

def check_and_download_viopms():
    # Bugünün tarihini al
    today_date = datetime.today().strftime('%Y%m%d')
    viopms_filename = f'EOD/BULTEN/viopms_{today_date}.csv'

    # Eğer dosya mevcut değilse veya tarihi bugüne ait değilse yeni dosya indir
    if not os.path.exists(viopms_filename):
        datastore = DataStore()
        datastore.auth()
        datastore.download_viopms_table()

        # İndirilen dosya ismini bulma
        downloaded_files = os.listdir('EOD/BULTEN')
        downloaded_file = [f for f in downloaded_files if f.startswith("viopms_") and f.endswith(".csv")]

        # Dosya adını ekrana yazdırma
        if downloaded_file:
            print(f"Indirilen dosya: {downloaded_file[0]}")
        else:
            print("İndirilen VIOPMS dosyası bulunamadı. DataStore indirirken bir hata olmuş olabilir.")

    return viopms_filename

def load_thb_data(thb_filename):
    # thb dosyasını yüklüyoruz
    thb_df = pd.read_csv(thb_filename, sep=';')
    thb_df.columns = thb_df.columns.str.replace(' +', ' ', regex=True)
    return thb_df

def load_viopms_data(viopms_filename):
    # viopms dosyasını doğru ayırıcı ile yüklüyoruz
    viopms_df = pd.read_csv(viopms_filename, sep=',', engine='python')
    viopms_df.columns = viopms_df.columns.str.strip()
    return viopms_df

def save_daily_data(df, filename):
    # Mevcut tarihi bir başlık satırı olarak ekleyip CSV dosyasına kaydeder
    today = datetime.today().strftime('%Y-%m-%d')
    with open(filename, 'w', newline='') as f:
        f.write(f"# Date: {today}\n")  # Tarih bilgisi başa eklenir
        df.to_csv(f, index=False)

def show_page():

    # Başlık ve açıklama
    st.title("Warrants List & Varantsız Spot İnceleme")
    st.write("Arkhon için gerekli warrant ve varantsız spot verilerini gösterir.")

    # Tarih seçimi
    future_option = st.selectbox("Lütfen bir tarih seçin:", ["310125", "280225"])

    # Güncel thb ve viopms dosyalarını al ve veriyi yükle
    thb_filename = check_and_download_thb()
    viopms_filename = check_and_download_viopms()
    thb_df = load_thb_data(thb_filename)
    viopms_df = load_viopms_data(viopms_filename)

    date_pattern = f"P{future_option}"

    # ---- Bölüm 1: warrants_list İşlemleri ----

    filtered_df = thb_df[(thb_df['BIST 100 ENDEKS'] == "1") & (thb_df['ISLEM KODU'].str.endswith('.E'))].copy()
    filtered_df[['ISLEM KODU']].to_csv('filtered_islem_kodu.csv', index=False)
    filtered_islem_kodu_df = pd.read_csv('filtered_islem_kodu.csv')
    matched_rows = pd.DataFrame(columns=['EQUITY', 'ISLEM KODU', 'STRIKE PRICE', 'CLOSING PRICE', 'FUTURE'])
    futures_set = set()

    for islem_kodu in filtered_islem_kodu_df['ISLEM KODU']:
        equity_name_with_e = islem_kodu.replace('.E', '') + '.E'
        equity_name = equity_name_with_e.replace('.E', '')
        matches = thb_df[
            thb_df['BULTEN ADI'].str.contains(equity_name) & thb_df['BULTEN ADI'].str.contains(date_pattern)].copy()

        if not matches.empty:
            matches['EQUITY'] = equity_name_with_e
            matches['STRIKE PRICE'] = matches['BULTEN ADI'].apply(
                lambda x: re.search(rf'{equity_name}{date_pattern}0*(\d+\.\d+)', x).group(1) if re.search(
                    rf'{equity_name}{date_pattern}0*(\d+\.\d+)', x) else None
            )
            closing_price = thb_df.loc[thb_df['ISLEM KODU'] == equity_name_with_e, 'KAPANIS FIYATI']
            if not closing_price.empty:
                matches['CLOSING PRICE'] = closing_price.values[0]

            # Future Bilgisini Ekleme
            future_filter = future_option[-4:]  # Örn: "0225" veya "0125"

            future_row = viopms_df[
                (viopms_df['DAYANAK VARLIK'] == equity_name_with_e) &
                (viopms_df['SOZLESME KODU'].str.contains(future_filter, na=False))
            ]

            if not future_row.empty:
                future_code = future_row.iloc[0]['SOZLESME KODU']
                matches['FUTURE'] = future_code
                futures_set.add(future_code)
            else:
                matches['FUTURE'] = None

            # 'FUTURE' sütununun olmadığı durumları kontrol et
            if 'FUTURE' not in matches.columns:
                matches['FUTURE'] = None

            required_columns = ['EQUITY', 'ISLEM KODU', 'STRIKE PRICE', 'CLOSING PRICE', 'FUTURE']
            for col in required_columns:
                if col not in matches.columns:
                    matches[col] = None

            matched_rows = pd.concat([matched_rows, matches[required_columns]])

    matched_rows['STRIKE PRICE'] = pd.to_numeric(matched_rows['STRIKE PRICE'], errors='coerce')
    matched_rows['CLOSING PRICE'] = pd.to_numeric(matched_rows['CLOSING PRICE'], errors='coerce')
    matched_rows['RATIO'] = ((matched_rows['STRIKE PRICE'] / matched_rows['CLOSING PRICE']) - 1).round(2)

    # Veriyi warrant_list.csv dosyasına kaydet
    save_daily_data(matched_rows, 'EOD/BULTEN/warrant_list.csv')

    # RATIO filtresi
    ratio_filter = st.selectbox("RATIO filtresi seçin:", ["Hepsi", "0 - 0.1", "0.1 - 0.2", "0.2 ve üzeri", "0'üzeri"])
    if ratio_filter == "0 - 0.1":
        filtered_warrants = matched_rows[(matched_rows['RATIO'] >= 0.00) & (matched_rows['RATIO'] <= 0.10)]
    elif ratio_filter == "0.1 - 0.2":
        filtered_warrants = matched_rows[(matched_rows['RATIO'] > 0.10) & (matched_rows['RATIO'] <= 0.20)]
    elif ratio_filter == "0.2 ve üzeri":
        filtered_warrants = matched_rows[matched_rows['RATIO'] > 0.20]
    elif ratio_filter == "0'üzeri":
        filtered_warrants = matched_rows[matched_rows['RATIO'] > 0]
    else:
        filtered_warrants = matched_rows

    # EQUITY seçimi
    equity_options = filtered_warrants['EQUITY'].unique().tolist()
    selected_equity = st.selectbox("Bir EQUITY değeri seçin:", ["Hepsi"] + equity_options)
    if selected_equity != "Hepsi":
        filtered_warrants = filtered_warrants[filtered_warrants['EQUITY'] == selected_equity]

    filtered_warrants.reset_index(drop=True, inplace=True)
    st.subheader("Warrants & Futures List")
    st.dataframe(filtered_warrants)

    # Liste oluşturma ve kopyalama
    if st.button("Listeyi Oluştur"):
        combined_list = filtered_warrants[['ISLEM KODU', 'FUTURE']].dropna().melt(value_name='Code')[
            'Code'].unique()
        combined_string = ",".join(combined_list)
        st.text("Warrant ve Future Listesi: " + combined_string)

        warrant_list = filtered_warrants['ISLEM KODU'].dropna().tolist()
        warrant_string = ",".join(warrant_list)
        st.write("Warrant Listesini Kopyala:")
        st_copy_to_clipboard(warrant_string)

        futures_list = filtered_warrants['FUTURE'].dropna().unique().tolist()
        futures_string = ",".join(futures_list)
        st.write("Future Listesini Kopyala:")
        st_copy_to_clipboard(futures_string)



    # ---- Bölüm 2: Varantsız Spot İşlemleri ----
    spot_list_file = 'spot_list.csv'
    spot_list_df = pd.read_csv(spot_list_file)
    spot_list_df.columns = spot_list_df.columns.str.strip()
    thb_df.columns = thb_df.columns.str.strip()

    not_found_data = []
    for index, row in spot_list_df.iterrows():
        underlying_asset = row['DAYANAK VARLIK']
        if thb_df['BULTEN ADI'].str.contains(underlying_asset, na=False).any():
            matched_rows = thb_df[thb_df['BULTEN ADI'].str.contains(underlying_asset, na=False)].copy()
            if not matched_rows['BULTEN ADI'].str.contains(future_option, na=False).any():
                not_found_data.append(row)
        else:
            not_found_data.append(row)

    not_found_df = pd.DataFrame(not_found_data)
    if not not_found_df.empty:
        not_found_df['BIST 100 ENDEKS'] = ''
        not_found_df['BIST 30 ENDEKS'] = ''
        for index, row in not_found_df.iterrows():
            underlying_asset = row['DAYANAK VARLIK'] + '.E'
            if thb_df['ISLEM KODU'].str.contains(underlying_asset, na=False).any():
                matched_rows = thb_df[thb_df['ISLEM KODU'].str.contains(underlying_asset, na=False)].copy()
                bist_100_value = matched_rows['BIST 100 ENDEKS'].iloc[0] if not matched_rows[
                    'BIST 100 ENDEKS'].empty else ''
                bist_30_value = matched_rows['BIST 30 ENDEKS'].iloc[0] if not matched_rows[
                    'BIST 30 ENDEKS'].empty else ''
                not_found_df.at[index, 'BIST 100 ENDEKS'] = bist_100_value
                not_found_df.at[index, 'BIST 30 ENDEKS'] = bist_30_value

    st.subheader(f"{future_option} Varantsız Spot")
    st.dataframe(not_found_df)
    save_daily_data(not_found_df, 'EOD/BULTEN/spot_list.csv')

    # ---- Bölüm 3: En Yüksek Strike Price ve Ratio Hesaplama ----

    filtered_df = thb_df[(thb_df['BIST 100 ENDEKS'] == "1") & (thb_df['ISLEM KODU'].str.endswith('.E'))].copy()
    filtered_df[['ISLEM KODU']].to_csv('filtered_islem_kodu.csv', index=False)
    filtered_islem_kodu_df = pd.read_csv('filtered_islem_kodu.csv')

    warrants_data = pd.DataFrame(columns=['EQUITY', 'ISLEM KODU', 'STRIKE PRICE', 'CLOSING PRICE', 'FUTURE'])
    futures_set = set()

    date_pattern = f"P{future_option}"

    for islem_kodu in filtered_islem_kodu_df['ISLEM KODU']:
        equity_name_with_e = islem_kodu.replace('.E', '') + '.E'
        equity_name = equity_name_with_e.replace('.E', '')
        matches = thb_df[
            thb_df['BULTEN ADI'].str.contains(equity_name) & thb_df['BULTEN ADI'].str.contains(date_pattern)
            ].copy()

        if not matches.empty:
            matches['EQUITY'] = equity_name_with_e
            matches['STRIKE PRICE'] = matches['BULTEN ADI'].apply(
                lambda x: re.search(rf'{equity_name}{date_pattern}0*(\d+\.\d+)', x).group(1) if re.search(
                    rf'{equity_name}{date_pattern}0*(\d+\.\d+)', x) else None
            )
            closing_price = thb_df.loc[thb_df['ISLEM KODU'] == equity_name_with_e, 'KAPANIS FIYATI']
            if not closing_price.empty:
                matches['CLOSING PRICE'] = closing_price.values[0]

            # Future Bilgisini Ekleme
            future_filter = future_option[-4:]
            future_row = viopms_df[
                (viopms_df['DAYANAK VARLIK'] == equity_name_with_e) &
                (viopms_df['SOZLESME KODU'].str.contains(future_filter, na=False))
                ]

            if not future_row.empty:
                future_code = future_row.iloc[0]['SOZLESME KODU']
                matches['FUTURE'] = future_code
                futures_set.add(future_code)
            else:
                matches['FUTURE'] = None

            warrants_data = pd.concat([
                warrants_data,
                matches[['EQUITY', 'ISLEM KODU', 'STRIKE PRICE', 'CLOSING PRICE', 'FUTURE']]
            ])

    # Sadece aynı equity değeri için en yüksek Strike Price'ı seç, aynı Strike Price'lı birden fazla varantı dahil et
    warrants_data['STRIKE PRICE'] = pd.to_numeric(warrants_data['STRIKE PRICE'], errors='coerce')
    warrants_data['CLOSING PRICE'] = pd.to_numeric(warrants_data['CLOSING PRICE'], errors='coerce')
    warrants_data['RATIO'] = ((warrants_data['STRIKE PRICE'] / warrants_data['CLOSING PRICE']) - 1).round(2)

    warrants_data = warrants_data[
        warrants_data['STRIKE PRICE'] == warrants_data.groupby('EQUITY')['STRIKE PRICE'].transform('max')]

    warrants_data.reset_index(drop=True, inplace=True)

    st.subheader("En Yüksek Strike Price")
    st.dataframe(warrants_data)

    save_daily_data(warrants_data, 'EOD/BULTEN/highest_strike_price.csv')

    if st.button("En Yüksek Strike Price için Listeyi Oluştur"):
        combined_list = warrants_data[['ISLEM KODU', 'FUTURE']].dropna().melt(value_name='Code')['Code'].unique()
        combined_string = ",".join(combined_list)
        st.text("Warrant ve Future Listesi: " + combined_string)

        warrant_list = warrants_data['ISLEM KODU'].dropna().tolist()
        warrant_string = ",".join(warrant_list)
        st.write("Warrant Listesini Kopyala:")
        st_copy_to_clipboard(warrant_string)

        futures_list = warrants_data['FUTURE'].dropna().unique().tolist()
        futures_string = ",".join(futures_list)
        st.write("Future Listesini Kopyala:")
        st_copy_to_clipboard(futures_string)

