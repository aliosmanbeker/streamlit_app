import streamlit as st
import pandas as pd
from playwright.sync_api import sync_playwright


def fetch_webpage(url, table_id):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_selector(f'table#{table_id}')

        table = page.query_selector(f'table#{table_id}')
        html = table.inner_html()
        browser.close()
        return html


def extract_table_data(html):
    # BeautifulSoup ile tablo verilerini ayrıştır
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    headers = [header.get_text(strip=True) for header in soup.find_all("th")]
    rows = []
    for row in soup.find_all("tr")[1:]:
        cells = [cell.get_text(strip=True) for cell in row.find_all("td")]
        rows.append(cells)
    return headers, rows


def save_to_csv(headers, rows, filename):
    if headers and rows:
        df = pd.DataFrame(rows, columns=headers)
        df.to_csv(filename, index=False)
        st.success(f"Tablo verileri {filename} dosyasına yazıldı.")
    else:
        st.error("Yazılacak veri bulunamadı.")


def show_sermaye_artirimi_page():
    st.title("Sermaye Artırımı Şirketleri")

    url = st.text_input("URL girin:",
                        "https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/Temel-Degerler-Ve-Oranlar.aspx?endeks=05#page-2")
    table_id = st.text_input("Tablo ID'si girin:", "DataTables_Table_0")
    csv_filename = st.text_input("CSV dosya adı:", "tablo_verileri.csv")

    if st.button("Verileri Çek ve Göster"):
        with st.spinner("Veriler çekiliyor..."):
            html = fetch_webpage(url, table_id)
            if html:
                headers, rows = extract_table_data(html)
                if headers and rows:
                    df = pd.DataFrame(rows, columns=headers)
                    st.subheader("Tablo Verileri")
                    st.dataframe(df)

                    if st.button("Verileri CSV'ye Kaydet"):
                        save_to_csv(headers, rows, csv_filename)
                else:
                    st.error("Tablo verileri çıkarılamadı.")
            else:
                st.error("Web sayfası yüklenemedi.")


if __name__ == "__main__":
    show_sermaye_artirimi_page()
