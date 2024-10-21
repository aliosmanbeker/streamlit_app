import pandas as pd
import streamlit as st

def show_page():
    # Streamlit başlığı
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

    # Her bir DAYANAK VARLIK için, thb dosyasındaki ISLEM  KODU sütununda .E ekleyerek arama yap
    for index, row in spot_list_df.iterrows():
        underlying_asset = row['DAYANAK VARLIK'] + ".E"  # .E ekleyerek arama yap

        # Eğer ISLEM  KODU sütununda underlying_asset bulunuyorsa
        if thb_df['ISLEM  KODU'].str.contains(underlying_asset, na=False).any():
            matched_rows = thb_df[thb_df['ISLEM  KODU'].str.contains(underlying_asset, na=False)]

            # Eğer BULTEN ADI içinde gelecekteki tarih (örneğin 1024) yoksa, spot'u not_found_data'ya ekle
            if not matched_rows['BULTEN ADI'].str.contains(future_option, na=False).any():
                # BIST 100 ENDEKS ve BIST 30 ENDEKS sütunlarını da ekleyerek veriyi listeye ekle
                not_found_data.append({
                    'DAYANAK VARLIK': row['DAYANAK VARLIK'],  # Orijinal DAYANAK VARLIK
                    'BIST 100 ENDEKS': matched_rows['BIST 100 ENDEKS'].values[0] if 'BIST 100 ENDEKS' in matched_rows.columns else None,
                    'BIST 30 ENDEKS': matched_rows['BIST 30 ENDEKS'].values[0] if 'BIST 30 ENDEKS' in matched_rows.columns else None
                })
        else:
            # Hiç bulunmazsa da not_found_data'ya ekle
            not_found_data.append({
                'DAYANAK VARLIK': row['DAYANAK VARLIK'],
                'BIST 100 ENDEKS': None,
                'BIST 30 ENDEKS': None
            })

    # Elde edilen verileri bir DataFrame'e dönüştürme
    not_found_df = pd.DataFrame(not_found_data)

    # Eşleşmeyen verileri yeni bir CSV dosyasına kaydetme
    not_found_df.to_csv(output_file, index=False)

    # Sonuçları Streamlit sayfasında gösterme
    st.write(f"Eşleşmeyen {future_option} verileri (Varantsız Spotlar) - BIST 100 ve BIST 30 ile birlikte:")
    st.dataframe(not_found_df)

    # CSV dosyasını indirme bağlantısı ekleme
    csv = not_found_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"{future_option} varantı olmayan verileri indir (CSV)",
        data=csv,
        file_name=output_file,
        mime='text/csv',
    )
