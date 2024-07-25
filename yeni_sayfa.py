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
        # Dosyayı yükleyin ve görüntüleyin
        file_path = f"datas/{selected_file}"
        try:
            df = pd.read_excel(file_path)
            df = df.reset_index(drop=True)  # Indeks numaralarını gizle
            st.dataframe(df.style.hide(axis='index'), height=800, width=1400)  # Genişliği %20 artırmak için
        except Exception as e:
            st.error(f"Dosya yüklenirken bir hata oluştu: {e}")
