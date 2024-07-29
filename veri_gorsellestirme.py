import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

def show_page():
    st.title("Şirket Verilerini Görselleştir")

    # CSV dosyasını yükle
    df = pd.read_csv('company_data.csv')

    # Veri Tabloları ve Filtreleme
    st.write('Veri Tablosu:')
    df = df.reset_index(drop=True)  # Indeks numaralarını gizle

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)  # Otomatik sayfa boyutu
    gb.configure_default_column(editable=True, groupable=True, filter=True)
    grid_options = gb.build()

    AgGrid(df, gridOptions=grid_options, height=800, width='100%')
