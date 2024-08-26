import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import os
from datetime import datetime, timedelta

CSV_FILENAME = "sermaye_artirimi_verileri.csv"
LAST_FETCHED_FILENAME = "last_fetched.txt"


def save_last_fetched_time():
    with open(LAST_FETCHED_FILENAME, "w") as f:
        f.write(datetime.now().isoformat())


def load_last_fetched_time():
    if os.path.exists(LAST_FETCHED_FILENAME):
        with open(LAST_FETCHED_FILENAME, "r") as f:
            return datetime.fromisoformat(f.read().strip())
    return None


def should_fetch_data():
    last_fetched = load_last_fetched_time()
    if last_fetched is None:
        return True
    return datetime.now() - last_fetched > timedelta(hours=24)


def fetch_data():
    # Tarayıcı ayarları
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    service = Service('path/to/chromedriver')  # Burada chromedriver yolunu belirtin
    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = "https://halkarz.com/sermaye-artirimi/"
    driver.get(url)

    # Tabloyu bul
    try:
        table = driver.find_element(By.CSS_SELECTOR, '.sal-bedelli .rwd-table')
        headers = [header.text.strip() for header in table.find_elements(By.CSS_SELECTOR, 'th')]

        rows = []
        for row in table.find_elements(By.CSS_SELECTOR, 'tr')[1:]:
            cells = [cell.text.strip() for cell in row.find_elements(By.CSS_SELECTOR, 'td')]
            if cells:
                rows.append(cells)

        df = pd.DataFrame(rows, columns=headers)
        driver.quit()
        return df
    except Exception as e:
        driver.quit()
        raise e


def show_page():
    st.title("Bedelli Sermaye Artırımı Yapacak Şirketler")

    if should_fetch_data():
        try:
            df = fetch_data()
            df.to_csv(CSV_FILENAME, index=False)
            save_last_fetched_time()
            st.success(f"Veriler güncellendi ve {CSV_FILENAME} dosyasına kaydedildi.")
        except Exception as e:
            st.error(f"Veri çekme işlemi başarısız oldu: {e}")
            return
    else:
        df = pd.read_csv(CSV_FILENAME)
        last_fetched = load_last_fetched_time()
        st.success(f"Veriler {last_fetched.strftime('%Y-%m-%d %H:%M:%S')} tarihinde çekildi.")

    st.dataframe(df)


if __name__ == "__main__":
    show_page()
