import pandas as pd
import streamlit as st


def show_varantsiz_spot_page():
    st.title("Varantsız Spot Verileri")

    # Seçenekler: 1024, 1124, 1224
    future_option = st.selectbox("Future Seçeneği Seçin", ['1024', '1124', '1224'])

    # Dosya adları
    spot_list_file = 'spot_list.csv'
    thb_file = 'EOD/BULTEN/thb202410181.csv'
    output_file = f'{future_option}_varantyok.csv'

    # Dosyaları okuma
    spot_list_df = pd.read_csv(spot_list_file)
    thb_df = pd.read_csv(thb_file, delimiter=';')

    # Sütun adlarını temizleme (boşlukları kaldırma)
    spot_list_df.columns = spot_list_df.columns.str.strip()
    thb_df.columns = thb_df.columns.str.strip()

    # Eşleşmeyen veriler için boş bir liste
    not_found_data = []

    # Varantsız spot listesi oluşturulacak ve sadece bu listeyi thb'de arayacağız
    for index, row in spot_list_df.iterrows():
        underlying_asset = row['DAYANAK VARLIK']

        # Eğer BULTEN ADI sütununda underlying_asset bulunuyorsa
        if thb_df['BULTEN ADI'].str.contains(underlying_asset, na=False).any():
            matched_rows = thb_df[thb_df['BULTEN ADI'].str.contains(underlying_asset, na=False)]

            # Eğer BULTEN ADI içinde future_option yoksa, spot'u not_found_data'ya ekle
            if not matched_rows['BULTEN ADI'].str.contains(future_option, na=False).any():
                not_found_data.append(row)
        else:
            # Hiç bulunmazsa da not_found_data'ya ekle
            not_found_data.append(row)

    # Elde edilen varantsız spot verileri için DataFrame'e dönüştürme
    not_found_df = pd.DataFrame(not_found_data)

    # Eğer varantsız spotlar varsa thb dosyasındaki ISLEM KODU sütunuyla eşleşenleri arıyoruz
    if not not_found_df.empty:
        # Yeni sütunlar ekleme (BIST 100 ve BIST 30 ENDEKS)
        not_found_df['BIST 100 ENDEKS'] = ''
        not_found_df['BIST 30 ENDEKS'] = ''

        for index, row in not_found_df.iterrows():
            underlying_asset = row['DAYANAK VARLIK'] + '.E'  # .E ekleyerek arama yapıyoruz

            # Eğer ISLEM  KODU sütununda underlying_asset bulunuyorsa
            if thb_df['ISLEM  KODU'].str.contains(underlying_asset, na=False).any():
                matched_rows = thb_df[thb_df['ISLEM  KODU'].str.contains(underlying_asset, na=False)]

                # BIST 100 ENDEKS ve BIST 30 ENDEKS sütunlarını ilgili satırlardan al
                bist_100_value = matched_rows['BIST 100 ENDEKS'].iloc[0] if not matched_rows[
                    'BIST 100 ENDEKS'].empty else ''
                bist_30_value = matched_rows['BIST 30 ENDEKS'].iloc[0] if not matched_rows[
                    'BIST 30 ENDEKS'].empty else ''

                # Mevcut satıra bu verileri ekle
                not_found_df.at[index, 'BIST 100 ENDEKS'] = bist_100_value
                not_found_df.at[index, 'BIST 30 ENDEKS'] = bist_30_value

    # Eşleşmeyen verileri yeni bir CSV dosyasına kaydetme
    not_found_df.to_csv(output_file, index=False)

    # Sonuçları Streamlit sayfasında gösterme
    st.write(f"Eşleşmeyen {future_option} verileri (Varantsız Spotlar):")
    st.dataframe(not_found_df)

    # CSV dosyasını indirme bağlantısı ekleme
    csv = not_found_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"{future_option} varantı olmayan verileri indir (CSV)",
        data=csv,
        file_name=output_file,
        mime='text/csv',
    )
