import streamlit as st
import pandas as pd


def show_page():
    st.title("Yeni Sayfa")

    # Veri Dosyalarını Seçin
    st.header("Veri Dosyalarını Seçin")

    dosya_secenekleri = [
        "Aşırı Hareket Senaryosu ve Kapsama Oranı (Extreme Move Multiplier and Extreme Move Covered Fraction).xlsx",
        "Fiyat Değişim Aralığı (Price Scan Range-PSR).xlsx",
        "Kısa Opsiyon Pozisyonu Minimum Riski (Short Option Minimum Risk).xlsx",
        "Ürün Grupları Arası Risk Analizi (Inter-Commodity Spread Credit).xlsx",
        "Vadeler Arası Yayılma Pozisyonu Riski (Intra-Commodity Spread Charge).xlsx"
    ]

    selected_file = st.radio("Dosya Seçin:", dosya_secenekleri)

    if selected_file:
        st.write(f"Seçilen Dosya: {selected_file}")

        # Dosya yolunu belirleyin
        file_path = f"datas/{selected_file}"

        try:
            # Dosyayı yükleyin ve yalnızca ilk iki sütunu alın
            df = pd.read_excel(file_path, usecols=[0, 1])  # İlk iki sütunu seçiyoruz

            # Indeks sütununu kaldırıyoruz
            df = df.reset_index(drop=True)

            # Her bir sütunun veri türünü ayarlıyoruz
            for column in df.columns:
                # Sadece sayısal veriler içeriyorsa float'a çevir
                if pd.to_numeric(df[column], errors='coerce').notna().all():
                    df[column] = pd.to_numeric(df[column], errors='coerce')
                else:
                    # Metin içeren sütunlar için string olarak ayarla
                    df[column] = df[column].astype(str)

            # Tüm hücreleri ortalamak için stil uygulayın
            styled_df = df.style.set_properties(**{'text-align': 'center'})  # Ortalamak için stil uygula
            styled_df.set_table_styles([{
                'selector': 'th',
                'props': [('text-align', 'center')]
            }])

            # Streamlit tablosu olarak göster
            st.table(styled_df)

        except Exception as e:
            st.error(f"Dosya yüklenirken bir hata oluştu: {e}")
