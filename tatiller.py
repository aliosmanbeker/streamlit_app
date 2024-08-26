import streamlit as st
import holidays
from datetime import datetime, timedelta
import pandas as pd

def get_date_ranges():
    today = datetime.today().date()

    # Haftanın başlangıcı ve bitişi
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    # Ayın başlangıcı ve bitişi
    month_start = today.replace(day=1)
    next_month = month_start.replace(day=28) + timedelta(days=4)
    month_end = next_month - timedelta(days=next_month.day)

    # Yılın başlangıcı ve bitişi
    year_start = today.replace(month=1, day=1)
    year_end = today.replace(month=12, day=31)

    return (week_start, week_end, month_start, month_end, year_start, year_end)


def get_holidays(year, date_range):
    turkey_holidays = holidays.Turkey(years=year)
    holidays_in_range = {date: name for date, name in turkey_holidays.items() if date_range[0] <= date <= date_range[1]}
    return holidays_in_range


def create_dataframe(holidays_dict):
    df = pd.DataFrame(holidays_dict.items(), columns=['Date', 'Holiday'])
    return df


def show_holidays_page():
    st.title("Türkiye'nin Tatilleri")

    # Tarih aralıklarını al
    week_start, week_end, month_start, month_end, year_start, year_end = get_date_ranges()

    current_year = datetime.today().year

    # Tatilleri al
    holidays_this_week = get_holidays(current_year, (week_start, week_end))
    holidays_this_month = get_holidays(current_year, (month_start, month_end))
    holidays_this_year = get_holidays(current_year, (year_start, year_end))

    # DataFrame oluştur
    df_week = create_dataframe(holidays_this_week)
    df_month = create_dataframe(holidays_this_month)
    df_year = create_dataframe(holidays_this_year)

    # Verileri göster
    st.subheader("Bu Hafta Tatilleri")
    st.dataframe(df_week)

    st.subheader("Bu Ay Tatilleri")
    st.dataframe(df_month)

    st.subheader("Bu Yıl Tatilleri")
    st.dataframe(df_year)


if __name__ == "__main__":
    show_holidays_page()
