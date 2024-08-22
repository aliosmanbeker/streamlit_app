import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd


def fetch_data():
    url = "https://halkarz.com/sermaye-artirimi/"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Bedelsiz sermaye artırımı ile ilgili tabloyu bul
        table = soup.select_one('.sal-bedelsiz .rwd-table')
        title_info = soup.select_one('.sal-bedelsiz .salb-title')

        if table and title_info:
            em_text = title_info.find('em').get_text(strip=True) if title_info.find('em') else '...'
            span_text = title_info.find('span').get_text(strip=True) if title_info.find('span') else '...'
            time_text = title_info.find('time').get_text(strip=True) if title_info.find('time') else '...'

            headers = [th.get_text(strip=True) for th in table.find_all('th')]
            rows = []

            for row in table.find_all('tr'):
                cols = row.find_all('td')
                if not cols:
                    continue

                bist_kodu = cols[0].find('a').get_text(strip=True) if cols[0].find('a') else '...'
                sirket_adi = cols[0].find('small').get_text(strip=True) if cols[0].find('small') else '...'
                ilk_sutun = f"{bist_kodu} - {sirket_adi}"

                yuzde = cols[1].get_text(strip=True) if len(cols) > 1 else '...'
                tutar = cols[2].get_text(strip=True) if len(cols) > 2 else '...'
                ruchan = cols[3].get_text(strip=True) if len(cols) > 3 else '...'
                ykk = cols[4].get_text(strip=True) if len(cols) > 4 else '...'

                if len(cols) > 5:
                    tarih_araligi = cols[5].get_text(strip=True) or '...'
                else:
                    tarih_araligi = '...'

                rows.append([ilk_sutun, yuzde, tutar, ruchan, ykk, tarih_araligi])

            df = pd.DataFrame(rows, columns=headers)
            return df, em_text, span_text, time_text
        else:
            return None, None, None, None
    else:
        return None, None, None, None


def show_page():
    st.title("Bedelsiz Sermaye Artırımı Yapacak Şirketler")

    df, em_text, span_text, time_text = fetch_data()

    if df is not None:
        st.subheader(em_text)
        st.write(f"Son güncelleme: {span_text} - {time_text}")
        st.dataframe(df)
    else:
        st.error("Veri çekilemedi.")


if __name__ == "__main__":
    show_page()
