import streamlit as st
import pandas as pd
import re
from st_copy_to_clipboard import st_copy_to_clipboard

def show_page():
    # Başlık ve açıklama
    st.title("Warrants List & Varantsız Spot İnceleme")
    st.write("CSV dosyalarındaki warrant ve spot bilgilerini görüntüleyin ve filtreleyin.")

    # Kullanıcının tarih seçimi yapabileceği bir seçenek
    future_option = st.selectbox("Lütfen bir tarih seçin:", ["291124", "311224"])

    # ---- Bölüm 1: warrants_list İşlemleri ----

    @st.cache_data
    def load_thb_data():
        thb_df = pd.read_csv('EOD/BULTEN/thb202411071.csv', sep=';')
        thb_df.columns = thb_df.columns.str.replace(' +', ' ', regex=True)
        return thb_df

    thb_df = load_thb_data()
    date_pattern = f"P{future_option}"

    # BIST 100 ENDEKS sütununda değeri 1 olan ve ISLEM KODU sütununda .E ile biten verileri filtrele
    filtered_df = thb_df[(thb_df['BIST 100 ENDEKS'] == "1") & (thb_df['ISLEM KODU'].str.endswith('.E'))].copy()
    filtered_df[['ISLEM KODU']].to_csv('filtered_islem_kodu.csv', index=False)
    filtered_islem_kodu_df = pd.read_csv('filtered_islem_kodu.csv')
    matched_rows = pd.DataFrame(columns=['EQUITY', 'ISLEM KODU', 'STRIKE PRICE', 'CLOSING PRICE'])

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
            closing_price = thb_df.loc[thb_df['ISLEM KODU'] == equity_name_with_e, 'ONCEKI KAPANIS FIYATI']
            if not closing_price.empty:
                matches['CLOSING PRICE'] = closing_price.values[0]
            matched_rows = pd.concat([matched_rows, matches[['EQUITY', 'ISLEM KODU', 'STRIKE PRICE', 'CLOSING PRICE']]])

    matched_rows['STRIKE PRICE'] = pd.to_numeric(matched_rows['STRIKE PRICE'], errors='coerce')
    matched_rows['CLOSING PRICE'] = pd.to_numeric(matched_rows['CLOSING PRICE'], errors='coerce')
    matched_rows['RATIO'] = ((matched_rows['STRIKE PRICE'] / matched_rows['CLOSING PRICE']) - 1).round(2)

    # RATIO filtresi
    ratio_filter = st.selectbox("RATIO filtresi seçin:", ["Hepsi", "0 - 0.1", "0.1 - 0.2", "0.2 ve üzeri"])
    if ratio_filter == "0 - 0.1":
        filtered_warrants = matched_rows[(matched_rows['RATIO'] >= 0.00) & (matched_rows['RATIO'] <= 0.10)]
    elif ratio_filter == "0.1 - 0.2":
        filtered_warrants = matched_rows[(matched_rows['RATIO'] > 0.10) & (matched_rows['RATIO'] <= 0.20)]
    elif ratio_filter == "0.2 ve üzeri":
        filtered_warrants = matched_rows[matched_rows['RATIO'] > 0.20]
    else:
        filtered_warrants = matched_rows

    # EQUITY değeri seçimi
    equity_options = filtered_warrants['EQUITY'].unique().tolist()
    selected_equity = st.selectbox("Bir EQUITY değeri seçin:", ["Hepsi"] + equity_options)

    # Seçilen EQUITY değerine göre filtreleme
    if selected_equity != "Hepsi":
        filtered_warrants = filtered_warrants[filtered_warrants['EQUITY'] == selected_equity]

    # Filtrelenmiş tabloyu her zaman gösteriyoruz
    st.subheader("Warrants List")
    filtered_warrants = filtered_warrants.reset_index(drop=True)
    st.dataframe(filtered_warrants)

    # Listeyi oluştur butonunu ekliyoruz, butona basıldığında ISLEM KODU listesi ve kopyalama butonu görünüyor
    if st.button("Warrants için Listeyi Oluştur"):
        # ISLEM KODU listesini hazırlıyoruz
        sozlesme_kodu_list = filtered_warrants['ISLEM KODU'].tolist()
        string_of_list = str(sozlesme_kodu_list).replace("'", "").replace("[", "").replace("]", "")

        # Listeyi ve kopyalama butonunu gösteriyoruz
        st.text("Warrant Listesi: " + string_of_list)
        st.text("Kopyalamak için aşağıdaki butona tıklayınız")
        st_copy_to_clipboard(string_of_list)

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
                bist_100_value = matched_rows['BIST 100 ENDEKS'].iloc[0] if not matched_rows['BIST 100 ENDEKS'].empty else ''
                bist_30_value = matched_rows['BIST 30 ENDEKS'].iloc[0] if not matched_rows['BIST 30 ENDEKS'].empty else ''
                not_found_df.at[index, 'BIST 100 ENDEKS'] = bist_100_value
                not_found_df.at[index, 'BIST 30 ENDEKS'] = bist_30_value

    st.subheader(f"{future_option} Varantsız Spot")
    not_found_df = not_found_df.reset_index(drop=True)
    st.dataframe(not_found_df)

    # ---- Bölüm 3: En Yüksek Strike Price İşlemleri ----
    @st.cache_data
    def load_thb_data():
        thb_df = pd.read_csv('EOD/BULTEN/thb202411071.csv', sep=';')
        thb_df.columns = thb_df.columns.str.replace(' +', ' ', regex=True)
        return thb_df

    thb_df = load_thb_data()
    date_pattern = f"P{future_option}"

    # Tabloyu her zaman görüntülemek için en yüksek strike price verilerini oluşturuyoruz
    filtered_df = thb_df[(thb_df['BIST 100 ENDEKS'] == "1") & (thb_df['ISLEM KODU'].str.endswith('.E'))].copy()
    filtered_df['ISLEM KODU'] = filtered_df['ISLEM KODU'].str.replace('.E', '', regex=False)
    filtered_df = filtered_df[['ISLEM KODU']].drop_duplicates().copy()
    warrants_data = []

    for i, row in filtered_df.iterrows():
        equity = row['ISLEM KODU']
        matches = thb_df[thb_df['BULTEN ADI'].str.contains(equity, na=False)].copy()
        warrant_rows = matches[matches['ENSTRUMAN GRUBU'] == 'EPW']
        max_strike_price = None
        selected_warrants = []

        for _, warrant_row in warrant_rows.iterrows():
            bulten_adi = warrant_row['BULTEN ADI']
            date_match = re.search(r'(\d{6})', bulten_adi)
            strike_price_match = re.search(r'(\d+\.\d+)', bulten_adi)

            if date_match and strike_price_match:
                date_part = date_match.group(1)
                strike_price = float(strike_price_match.group(1))
                if date_part.endswith(future_option):
                    if max_strike_price is None or strike_price > max_strike_price:
                        max_strike_price = strike_price
                        selected_warrants = [warrant_row['ISLEM KODU']]
                    elif strike_price == max_strike_price:
                        selected_warrants.append(warrant_row['ISLEM KODU'])

        for warrant in selected_warrants:
            warrants_data.append({
                'ISLEM KODU': equity,
                'WARRANT': warrant,
            })

    # Tabloyu göstermek için DataFrame'e dönüştürüyoruz ve Streamlit ile gösteriyoruz
    highest_strike_df = pd.DataFrame(warrants_data)
    st.subheader("En Yüksek Strike Price")
    highest_strike_df = highest_strike_df.reset_index(drop=True)
    st.dataframe(highest_strike_df)

    # Listeyi oluştur butonunu ekliyoruz, butona basıldığında warrant isimleri ve kopyalama butonu görüntüleniyor
    if st.button("En Yüksek Strike Price için Listeyi Oluştur"):
        # Listeyi hazırlıyoruz
        sozlesme_kodu_list = highest_strike_df['WARRANT'].tolist()
        string_of_list = str(sozlesme_kodu_list).replace("'", "").replace("[", "").replace("]", "")

        # Listeyi ve kopyalama butonunu gösteriyoruz
        st.text("En Yüksek Strike Price Listesi: " + string_of_list)
        st.text("Kopyalamak için aşağıdaki butona tıklayınız")
        st_copy_to_clipboard(string_of_list)