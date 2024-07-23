import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO


def get_tick_size(price):
    if price < 20.00:
        return 0.01
    elif price < 50.00:
        return 0.02
    elif price < 100.00:
        return 0.05
    elif price < 250.00:
        return 0.1
    elif price < 500.00:
        return 0.25
    elif price < 1000.00:
        return 0.5
    elif price < 2500.00:
        return 1.0
    else:
        return 2.5


def detect_all_tick_jumps(df, tick_multiplier=3, time_window_ms=100):
    checked_indices = set()
    results = []
    for i in range(len(df)):
        if i in checked_indices:
            continue
        current_row = df.iloc[i]
        tick_size = get_tick_size(current_row['askPrice'])
        tick_jump = tick_multiplier * tick_size
        # Kullanıcının girdiği milisaniye cinsinden zaman penceresi
        time_window = df[(df['timestamp'] >= current_row['timestamp']) & (
                df['timestamp'] <= current_row['timestamp'] + pd.Timedelta(milliseconds=time_window_ms))]

        if len(time_window) > 0 and (time_window['askPrice'].max() - current_row['askPrice'] >= tick_jump):
            initial_price = current_row['askPrice']
            initial_time = current_row['timestamp']
            max_price = initial_price
            max_time = initial_time
            price_rows = []
            for j in range(i + 1, len(df)):
                future_row = df.iloc[j]
                checked_indices.add(j)
                price_rows.append((future_row['timestamp'], future_row['askPrice']))
                if future_row['askPrice'] > max_price:
                    max_price = future_row['askPrice']
                    max_time = future_row['timestamp']
                if future_row['askPrice'] < initial_price:
                    break
            results.append({
                'initial_time': initial_time,
                'initial_price': initial_price,
                'max_time': max_time,
                'max_price': max_price,
                'price_rows': price_rows
            })
    return results


def show_page():
    st.title("Yükseliş Takip Stratejisi")

    file_options = [
        'yukselis/bist_20240227_ISCTR.E_trades.csv',
        'yukselis/bist_20240209_TSKB.E_trades.csv',
        'yukselis/bist_20240215_TSKB.E_trades.csv',
        'yukselis/bist_20240222_TSKB.E_trades.csv',
        'yukselis/bist_20240227_TSKB.E_trades.csv'
    ]

    file_path = st.selectbox("Dosya Seçin", file_options)
    tick_multiplier = st.number_input("Tick Multiplier", min_value=1, max_value=10, value=3)
    time_window_ms = st.number_input("Zaman Penceresi (ms)", min_value=1, max_value=1000, value=100)

    if st.button("Analizi Başlat"):
        data = pd.read_csv(file_path)
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ns')
        data.sort_values(by='timestamp', inplace=True)

        results = detect_all_tick_jumps(data, tick_multiplier=tick_multiplier, time_window_ms=time_window_ms)

        for idx, result in enumerate(results):
            # Zaman ve fiyat bilgilerini Streamlit'te göster
            st.write(f"Başlangıç Zamanı: {result['initial_time']}, Başlangıç Fiyatı: {result['initial_price']}")
            st.write(f"Maksimum Zaman: {result['max_time']}, Maksimum Fiyat: {result['max_price']}")

            times = [result['initial_time']] + [row[0] for row in result['price_rows']]
            prices = [result['initial_price']] + [row[1] for row in result['price_rows']]

            plt.figure(figsize=(12, 6))
            plt.plot(times, prices, marker='o')
            plt.title(
                f"Başlangıç Zamanı: {result['initial_time']}, Başlangıç Fiyatı: {result['initial_price']}\nMaksimum Zaman: {result['max_time']}, Maksimum Fiyat: {result['max_price']}")
            plt.xlabel('Zaman')
            plt.ylabel('Fiyat (TL)')
            plt.grid(True)

            buf = BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            st.image(buf, caption=f"Tick Jump Plot {idx}")
            plt.close()


