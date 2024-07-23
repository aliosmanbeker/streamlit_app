import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import subprocess
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# CSV dosyasını yükle
df = pd.read_csv('company_data.csv')

# Sayfa navigasyonu
st.sidebar.title("Navigasyon")
selected_page = st.sidebar.radio("Sayfa seçin:", ["Ana Sayfa", "Veri Görselleştirme", "Backtest Analizi"])

# Ana Sayfa
if selected_page == "Ana Sayfa":
    st.title("Hoşgeldiniz")
    st.write("""
        Bu uygulama, şirket verilerini görselleştirmek için tasarlanmıştır.
        Soldaki menüyü kullanarak farklı sayfalara geçebilirsiniz.
    """)

# Veri Görselleştirme Sayfası
elif selected_page == "Veri Görselleştirme":
    st.title("Şirket Verilerini Görselleştir")


    # Sayfalama için gerekli fonksiyon
    def get_table_page(dataframe, page_size, page_num):
        start_index = page_num * page_size
        end_index = start_index + page_size
        return dataframe.iloc[start_index:end_index]


    # Sayfa boyutunu ve sayfa numarasını belirleyin
    page_size = st.sidebar.number_input('Sayfa Boyutu', min_value=5, max_value=100, value=20, step=5)
    page_num = st.sidebar.number_input('Sayfa Numarası', min_value=0, max_value=len(df) // page_size, step=1)

    # Veri Tabloları ve Filtreleme
    st.write('Veri Tablosu:')
    paged_df = get_table_page(df, page_size, page_num)
    st.write(paged_df)

    # Borsada İşlem Görüp Görmediğine Göre Filtreleme
    st.sidebar.header('Filtreler')
    borsada_islem = st.sidebar.multiselect('Borsada İşlem Görme Durumu Seçin:',
                                           df['Borsada işlem görüp görmediği'].unique())
    pay_grubu = st.sidebar.multiselect('Pay Grubu Seçin:', df['Pay Grubu'].unique())

    filtered_df = df
    if borsada_islem:
        filtered_df = filtered_df[filtered_df['Borsada işlem görüp görmediği'].isin(borsada_islem)]
    if pay_grubu:
        filtered_df = filtered_df[filtered_df['Pay Grubu'].isin(pay_grubu)]

    st.write('Filtrelenmiş Veri Tablosu:')
    filtered_paged_df = get_table_page(filtered_df, page_size, page_num)
    st.write(filtered_paged_df)

    # Borsada işlem görüp görmeme durumu grafiği
    st.subheader('Borsada İşlem Görme Durumu:')
    borsa_gorme = df['Borsada işlem görüp görmediği'].value_counts()
    st.bar_chart(borsa_gorme)

    # Pay Grubu Dağılımı (En fazla verisi olan 5 kategori)
    st.subheader('Pay Grubu Dağılımı:')
    pay_grubu_sayim = df['Pay Grubu'].value_counts().nlargest(5)
    fig, ax = plt.subplots()
    ax.pie(pay_grubu_sayim, labels=pay_grubu_sayim.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

    # İmtiyaz Türü Dağılımı (En fazla verisi olan 5 kategori)
    st.subheader('İmtiyaz Türü Dağılımı:')
    imtiyaz_turu_sayim = df['İmtiyaz Türü'].value_counts().nlargest(5)
    fig, ax = plt.subplots()
    ax.pie(imtiyaz_turu_sayim, labels=imtiyaz_turu_sayim.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)


# Backtest Analizi Sayfası
elif selected_page == "Backtest Analizi":
    st.title("Backtest Analizi")

    # backtest.py dosyasını çalıştır
    result = subprocess.run(['python', 'kapanısta_al_acılısta_sat/backtest.py'], capture_output=True, text=True)

    if result.returncode == 0:
        st.success("Backtest başarıyla tamamlandı.")
        st.plotly_chart(go.Figure(go.Scatter(x=[], y=[])))  # Dummy plot
    else:
        st.error("Backtest çalıştırılamadı.")
        st.error(result.stderr)
