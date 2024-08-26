import streamlit as st
from playwright.async_api import async_playwright
import pandas as pd
import asyncio
import os
import datetime

# CSV dosyası için yol
CSV_FILE_PATH = 'bedelsiz_sermaye_artirimi_data.csv'

async def fetch_data():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Web sayfasını ziyaret et ve yüklendiğini bekle
        url = "https://halkarz.com/sermaye-artirimi/"
        await page.goto(url, wait_until="load", timeout=60000)

        # Sayfanın tamamen yüklendiğinden emin olun
        await page.wait_for_selector('.sal-bedelsiz .rwd-table', timeout=60000)

        # Seçicinin var olup olmadığını kontrol et
        table = await page.query_selector('.sal-bedelsiz .rwd-table')
        title_info = await page.query_selector('.sal-bedelsiz .salb-title')

        if table and title_info:
            # Em ve Span etiketi içerisindeki verileri çekiyoruz
            em_text = await title_info.eval_on_selector('em', 'el => el.textContent') or '...'
            span_text = await title_info.eval_on_selector('span', 'el => el.textContent') or '...'
            time_text = await title_info.eval_on_selector('time', 'el => el.textContent') or '...'

            # Başlıkları (headers) otomatik olarak ilk <th> etiketlerinden çekiyoruz
            headers = await table.eval_on_selector_all('tr th', 'els => els.map(el => el.textContent.trim())')

            # Verileri çekiyoruz
            rows = []
            for row in await table.query_selector_all('tr'):
                cols = await row.query_selector_all('td')

                if not cols:
                    continue

                # İlk sütun: Bist Kodu ve Şirket Adı birleştiriliyor
                bist_kodu = await cols[0].eval_on_selector('a', 'el => el.textContent') or '...'
                sirket_adi = await cols[0].eval_on_selector('small', 'el => el.textContent') or '...'
                ilk_sutun = f"{bist_kodu} - {sirket_adi}"

                # Diğer sütunlar sırayla
                yuzde = await cols[1].text_content() or '...'
                tutar = await cols[2].text_content() or '...'
                ruchan = await cols[3].text_content() or '...'
                ykk = await cols[4].text_content() or '...'

                # Son sütun: Başlangıç ve bitiş tarihleri
                if len(cols) > 5:
                    tarih_araligi = await cols[5].text_content() or '...'
                else:
                    tarih_araligi = '...'

                # Verileri sıralı bir şekilde ekliyoruz
                rows.append([ilk_sutun, yuzde, tutar, ruchan, ykk, tarih_araligi])

            # Verileri DataFrame'e dönüştürme
            df = pd.DataFrame(rows, columns=headers)

            await browser.close()
            return df, em_text, span_text, time_text
        else:
            await browser.close()
            return None, None, None, None

def save_data_to_csv(df, em_text, span_text, time_text):
    # Verileri CSV dosyasına kaydet
    df['Son Güncelleme Em'] = em_text
    df['Son Güncelleme Span'] = span_text
    df['Son Güncelleme Tarihi'] = time_text
    df['Çekilme Tarihi'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df.to_csv(CSV_FILE_PATH, index=False)

def load_data_from_csv():
    # CSV dosyasından verileri yükle
    if os.path.exists(CSV_FILE_PATH):
        df = pd.read_csv(CSV_FILE_PATH)
        return df
    return None

def is_data_outdated():
    # Verilerin eski olup olmadığını kontrol et
    if os.path.exists(CSV_FILE_PATH):
        df = pd.read_csv(CSV_FILE_PATH)
        last_fetch_time = df['Çekilme Tarihi'].iloc[0]
        last_fetch_time = datetime.datetime.strptime(last_fetch_time, '%Y-%m-%d %H:%M:%S')
        current_time = datetime.datetime.now()
        time_diff = current_time - last_fetch_time
        return time_diff.total_seconds() > 86400  # 24 saat
    return True

def show_page():
    st.title("Bedelsiz Sermaye Artırımı Yapacak Şirketler")

    max_attempts = 3
    attempt = 0
    success = False

    # Verilerin güncel olup olmadığını kontrol et
    if is_data_outdated():
        while attempt < max_attempts and not success:
            try:
                # Verileri çek
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                df, em_text, span_text, time_text = loop.run_until_complete(fetch_data())

                if df is not None:
                    save_data_to_csv(df, em_text, span_text, time_text)
                    success = True
                else:
                    st.error(f"Veri çekilemedi. Deneme {attempt + 1}.")
                    attempt += 1
            except Exception as e:
                st.error(f"Hata oluştu: {str(e)}. Deneme {attempt + 1}.")
                attempt += 1

    # CSV dosyasından verileri yükle ve göster
    df = load_data_from_csv()
    if df is not None:
        # Başlık ve tarih bilgilerini sayfada göster
        st.subheader(df['Son Güncelleme Em'].iloc[0])
        st.write(f"Son güncelleme: {df['Son Güncelleme Span'].iloc[0]} - {df['Son Güncelleme Tarihi'].iloc[0]}")

        # Gereksiz sütunları sil
        df = df.drop(columns=['Son Güncelleme Em', 'Son Güncelleme Span', 'Son Güncelleme Tarihi', 'Çekilme Tarihi'])

        # Verileri tablo olarak göster
        st.dataframe(df)
    else:
        st.error("Veri yüklenemedi.")

if __name__ == "__main__":
    show_page()
