import streamlit as st
import pandas as pd

def show_page():
    st.title("Yeni Sayfa")

    st.sidebar.title("Veri Dosyalarını Seçin")

    # Toggle butonları
    dosya_secenekleri = [
        "Aşırı Hareket Senaryosu ve Kapsama Oranı (Extreme Move Multiplier and Extreme Move Covered Fraction).xlsx",
        "Fiyat Değişim Aralığı (Price Scan Range-PSR).xlsx",
        "Kısa Opsiyon Pozisyonu Minimum Riski (Short Option Minimum Risk).xlsx",
        "Ürün Grupları Arası Risk Analizi (Inter-Commodity Spread Credit).xlsx",
        "Vadeler Arası Yayılma Pozisyonu Riski (Intra-Commodity Spread Charge).xlsx"
    ]

    selected_file = st.sidebar.radio("Dosya Seçin:", dosya_secenekleri)

    if selected_file:
        st.write(f"Seçilen Dosya: {selected_file}")
        # Dosyayı yükleyin ve görüntüleyin
        file_path = f"datas/{selected_file}"
        try:
            df = pd.read_excel(file_path)
            st.dataframe(df)
        except Exception as e:
            st.error(f"Dosya yüklenirken bir hata oluştu: {e}")