import streamlit as st
from kapanısta_al_acılısta_sat.backtest import analyze_data

def show_page():
    st.title("Kapanışta Al Açılışta Sat Stratejisi")

    input_file = 'kapanısta_al_acılısta_sat/F_XU0300624_trades_1min.txt'

    fig = analyze_data(input_file)

    if fig:
        st.plotly_chart(fig)
    else:
        st.error("Grafik oluşturulamadı.")
