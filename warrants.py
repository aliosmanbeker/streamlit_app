import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

def show_page():
    st.title("Warrants Verisi")

    # CSV dosyasını yükle
    file_path = '2024-07-27T09-49_export_final.csv'
    try:
        df = pd.read_csv(file_path)
        df = df.reset_index(drop=True)  # Indeks numaralarını gizle

        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination()
        gb.configure_default_column(editable=True, groupable=True, filter=True)
        grid_options = gb.build()

        AgGrid(df, gridOptions=grid_options, height=800, width='100%')
    except Exception as e:
        st.error(f"Dosya yüklenirken bir hata oluştu: {e}")
