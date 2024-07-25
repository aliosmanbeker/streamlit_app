import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def show_page():
    st.title("Şirket Verilerini Görselleştir")

    # CSV dosyasını yükle
    df = pd.read_csv('company_data.csv')

    # Sayfa boyutunu ve sayfa numarasını belirleyin
    st.header('Sayfa Ayarları')
    page_size = st.number_input('Sayfa Boyutu', min_value=5, max_value=100, value=20, step=5)
    page_num = st.number_input('Sayfa Numarası', min_value=0, max_value=len(df) // page_size, step=1)

    # Sayfalama için gerekli fonksiyon
    def get_table_page(dataframe, page_size, page_num):
        start_index = page_num * page_size
        end_index = start_index + page_size
        return dataframe.iloc[start_index:end_index]

    # Veri Tabloları ve Filtreleme
    st.write('Veri Tablosu:')
    paged_df = get_table_page(df, page_size, page_num)
    st.dataframe(paged_df, height=800, width=1400)  # Genişliği %20 artırmak için

    # Borsada İşlem Görüp Görmediğine Göre Filtreleme
    st.header('Filtreler')
    borsada_islem = st.multiselect('Borsada İşlem Görme Durumu Seçin:', df['Borsada işlem görüp görmediği'].unique())
    pay_grubu = st.multiselect('Pay Grubu Seçin:', df['Pay Grubu'].unique())

    filtered_df = df
    if borsada_islem:
        filtered_df = filtered_df[filtered_df['Borsada işlem görüp görmediği'].isin(borsada_islem)]
    if pay_grubu:
        filtered_df = filtered_df[filtered_df['Pay Grubu'].isin(pay_grubu)]

    st.write('Filtrelenmiş Veri Tablosu:')
    filtered_paged_df = get_table_page(filtered_df, page_size, page_num)
    st.dataframe(filtered_paged_df, height=800, width=1400)  # Genişliği %20 artırmak için

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

    # Korelasyon Matrisi
    st.subheader('Korelasyon Matrisi:')
    # Sadece sayısal sütunları seçin
    numeric_df = df.select_dtypes(include='number')
    if not numeric_df.empty:
        corr_matrix = numeric_df.corr()
        st.write(corr_matrix)
        fig, ax = plt.subplots()
        cax = ax.matshow(corr_matrix, cmap='coolwarm')
        fig.colorbar(cax)
        st.pyplot(fig)
    else:
        st.write("Korelasyon matrisi oluşturmak için yeterli sayısal veri yok.")
