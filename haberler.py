import os
import pandas as pd
from datetime import datetime
from playwright.sync_api import sync_playwright
import streamlit as st

# CSV dosyası için yol
CSV_FILE_PATH = 'haftalik_ekonomik_takvim.csv'


def fetch_data():
    url = "https://galatamenkul.com/arastirma/haftalik-ekonomik-takvim/"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state('networkidle')  # Sayfanın tamamen yüklenmesini bekler
        content = page.content()

    # Tablodaki veriyi çekerken
    df = pd.read_html(content)[0]

    # Son 8 sütundaki boş 'td' etiketlerini dikkate almamak için bu sütunları kaldırıyoruz
    if len(df.columns) > 8:
        df = df.iloc[:, :-8]

    # Unnamed sütunları da kaldırmak için
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    # Çekilme tarihini ekleme
    df['Çekilme Tarihi'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return df


def save_data_to_csv(df):
    df.to_csv(CSV_FILE_PATH, index=False)


def load_data_from_csv():
    if os.path.exists(CSV_FILE_PATH):
        df = pd.read_csv(CSV_FILE_PATH)
        return df
    return None


def is_data_outdated():
    if os.path.exists(CSV_FILE_PATH):
        df = pd.read_csv(CSV_FILE_PATH)
        last_fetch_time = df['Çekilme Tarihi'].iloc[0]
        last_fetch_time = datetime.strptime(last_fetch_time, '%Y-%m-%d %H:%M:%S')
        current_time = datetime.now()
        time_diff = current_time - last_fetch_time
        return time_diff.total_seconds() > 86400  # 24 saat
    return True


def get_weekly_news():
    if is_data_outdated():
        df = fetch_data()
        save_data_to_csv(df)
    else:
        df = load_data_from_csv()
    return df


def show_haberler_page():
    st.title("Haftalık Ekonomik Takvim")

    df = get_weekly_news()

    if df is not None:
        st.write(f"Son güncelleme: {df['Çekilme Tarihi'].iloc[0]}")
        df = df.drop(columns=['Çekilme Tarihi'])
        st.dataframe(df)
    else:
        st.error("Veri yüklenemedi.")


if __name__ == "__main__":
    show_haberler_page()
