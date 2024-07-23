import pandas as pd
import matplotlib.pyplot as plt

file_path = 'yukselis/bist_20240227_ISCTR.E_trades.csv'
data = pd.read_csv(file_path)

data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ns')
data.sort_values(by='timestamp', inplace=True)

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

def detect_all_tick_jumps(df, tick_multiplier=3):
    checked_indices = set()
    results = []
    for i in range(len(df)):
        if i in checked_indices:
            continue
        current_row = df.iloc[i]
        tick_size = get_tick_size(current_row['askPrice'])
        tick_jump = tick_multiplier * tick_size
        # 0.1 saniye içinde belirli tick sayısında artış olup olmadığını kontrol et
        time_window = df[(df['timestamp'] >= current_row['timestamp']) & (
                    df['timestamp'] <= current_row['timestamp'] + pd.Timedelta(milliseconds=100))]

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

# Bu fonksiyonun çıktısını Streamlit'te kullanacağız
results = detect_all_tick_jumps(data)



file_path = 'yukselis/bist_20240227_ISCTR.E_trades.csv'