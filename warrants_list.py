import pandas as pd
import streamlit as st


def show_page():
    # Streamlit başlığı
    st.title("Varantsız Spot Verileri")

    # Seçenekler: 1024, 1124, 1224
    future_option = st.selectbox("Future Seçeneği Seçin", ['1024', '1124', '1224'])

    # Dosya adları
    spot_list_file = f'{future_option}_varantyok.csv'  # Varantı olmayan spotlar dosyası
    thb_file = 'EOD/BULTEN/thb202410181.csv'

    # Dosyaları okuma
    spot_list_df = pd.read_csv(spot_list_file)
    thb_df = pd.read_csv(thb_file, delimiter=';')

    # Sütun adlarını temizleme (boşlukları kaldırma)
    spot_list_df.columns = spot_list_df.columns.str.strip()
    thb_df.columns = thb_df.columns.str.strip()

    # Varantı olmayan spotlar için boş bir liste
    updated_spot_list = []

    # Varantı olmayan her bir spot için arama yap ve BIST 100 ve BIST 30 verilerini ekle
    for index, row in spot_list_df.iterrows():
        underlying_asset_with_e = row['DAYANAK VARLIK'] + ".E"  # .E ekleyerek arama yap

        # ISLEM  KODU sütununda underlying_asset_with_e değerini arıyoruz
        matched_rows = thb_df[thb_df['ISLEM  KODU'].str.contains(underlying_asset_with_e, na=False)]

        if not matched_rows.empty:
            # Eşleşen satırların BIST 100 ENDEKS ve BIST 30 ENDEKS bilgilerini al ve listeye ekle
            updated_spot_list.append({
                'DAYANAK VARLIK': row['DAYANAK VARLIK'],
                'BIST 100 ENDEKS': matched_rows['BIST 100 ENDEKS'].values[
                    0] if 'BIST 100 ENDEKS' in matched_rows.columns else None,
                'BIST 30 ENDEKS': matched_rows['BIST 30 ENDEKS'].values[
                    0] if 'BIST 30 ENDEKS' in matched_rows.columns else None
            })
        else:
            # Eğer bulunmazsa boş olarak ekle
            updated_spot_list.append({
                'DAYANAK VARLIK': row['DAYANAK VARLIK'],
                'BIST 100 ENDEKS': None,
                'BIST 30 ENDEKS': None
            })

    # Elde edilen verileri bir DataFrame'e dönüştürme
    updated_spot_df = pd.DataFrame(updated_spot_list)

    # Sonuçları Streamlit sayfasında gösterme
    st.write(f"Varantı olmayan spotların {future_option} için BIST 100 ve BIST 30 bilgileri:")
    st.dataframe(updated_spot_df)

    # CSV dosyasını indirme bağlantısı ekleme
    csv = updated_spot_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"{future_option} varantı olmayan verileri indir (CSV)",
        data=csv,
        file_name=f'{future_option}_varantyok_bist.csv',
        mime='text/csv',
    )
