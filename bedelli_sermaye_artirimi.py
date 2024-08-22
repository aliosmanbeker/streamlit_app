import streamlit as st
from playwright.async_api import async_playwright
import pandas as pd
import asyncio


async def fetch_data():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Web sayfasını ziyaret et
        url = "https://halkarz.com/sermaye-artirimi/"
        await page.goto(url)

        # Sayfanın tamamen yüklendiğinden emin olun
        await page.wait_for_load_state('networkidle')

        # Seçicinin var olup olmadığını kontrol et
        table = await page.query_selector('.sal-bedelli .rwd-table')
        title_info = await page.query_selector('.sal-bedelli .salb-title')

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
                spk_onay = await cols[5].text_content() or '...'

                # Son sütun: Başlangıç ve bitiş tarihleri
                if len(cols) > 6:
                    tarih_araligi = await cols[6].text_content() or '...'
                else:
                    tarih_araligi = '...'

                # Verileri sıralı bir şekilde ekliyoruz
                rows.append([ilk_sutun, yuzde, tutar, ruchan, ykk, spk_onay, tarih_araligi])

            # Verileri DataFrame'e dönüştürme ve sıralama
            df = pd.DataFrame(rows, columns=headers)

            await browser.close()
            return df, em_text, span_text, time_text
        else:
            await browser.close()
            return None, None, None, None


def show_page():
    st.title("Bedelli Sermaye Artırımı Yapacak Şirketler")

    # Verileri çek
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    df, em_text, span_text, time_text = loop.run_until_complete(fetch_data())

    if df is not None:
        # Başlık ve tarih bilgilerini sayfada göster
        st.subheader(em_text)
        st.write(f"Son güncelleme: {span_text} - {time_text}")

        # Verileri tablo olarak göster
        st.dataframe(df)
    else:
        st.error("Veri çekilemedi.")


if __name__ == "__main__":
    show_page()
