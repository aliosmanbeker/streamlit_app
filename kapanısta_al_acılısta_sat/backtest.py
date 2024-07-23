import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

def find_closest_time(group, target_time, direction='forward'):
    """Find the closest time to target_time in the group."""
    times = group['Datetime'].dt.time
    if direction == 'forward':
        valid_times = times[times >= target_time]
        if not valid_times.empty:
            closest_time = valid_times.min()
        else:
            closest_time = times.max()
    else:
        valid_times = times[times <= target_time]
        if not valid_times.empty:
            closest_time = valid_times.max()
        else:
            closest_time = times.min()
    closest_row = group.loc[group['Datetime'].dt.time == closest_time]
    return closest_row

def analyze_data(input_file):
    # Veri setini yükle
    data = pd.read_csv(input_file, delimiter=',')

    # Tarih ve saat sütunlarını birleştirerek datetime objesine dönüştür
    data['Datetime'] = pd.to_datetime(data['TARIH'], format='%Y-%m-%d %H:%M:%S')
    data['Date'] = data['Datetime'].dt.date
    grouped = data.groupby('Date')

    # Fiyat farklarını ve yüzde değişimleri hesapla
    diffs_close = []
    percentage_changes_1730_1800 = []
    percentage_changes_close_open = []
    dates = []

    # Tüm mevcut tarihleri içeren bir liste oluştur
    all_dates = data['Date'].drop_duplicates().sort_values().tolist()

    for i in range(len(all_dates) - 1):
        current_date = all_dates[i]
        next_date = all_dates[i + 1]

        current_group = grouped.get_group(current_date)
        next_group = grouped.get_group(next_date)

        # Kapanış fiyatı için 17:59 veya en yakın daha önceki zamanı bul
        target_close_time = datetime.strptime('17:59:00', '%H:%M:%S').time()
        close_row = find_closest_time(current_group, target_close_time, direction='backward')
        if close_row.empty:
            continue
        close_price = close_row['FIYAT'].values[0]

        # Açılış fiyatı için 10:00 veya en yakın sonraki zamanı bul
        target_open_time = datetime.strptime('10:00:00', '%H:%M:%S').time()
        open_row = find_closest_time(next_group, target_open_time, direction='forward')
        if open_row.empty:
            continue
        open_price = open_row['FIYAT'].values[0]

        # Fiyat farkını hesapla ve sakla
        diffs_close.append(close_price - open_price)
        dates.append(next_date)

        # 17:30 açılış ve 18:00 kapanış arasındaki yüzdesel değişimi hesapla
        open_time_1730 = find_closest_time(current_group, datetime.strptime('17:30:00', '%H:%M:%S').time(), direction='forward')
        close_time_1800 = find_closest_time(current_group, datetime.strptime('18:00:00', '%H:%M:%S').time(), direction='backward')
        if open_time_1730.empty or close_time_1800.empty:
            continue
        open_price_1730 = open_time_1730['FIYAT'].values[0]
        close_price_1800 = close_time_1800['FIYAT'].values[0]
        percentage_change_1730_1800 = ((close_price_1800 - open_price_1730) / open_price_1730) * 100
        percentage_changes_1730_1800.append(percentage_change_1730_1800)

        # 10:00 açılış ve 17:59 kapanış arasındaki yüzdesel değişimi hesapla
        if open_price != 0:  # 0'a bölünme hatasını önle
            percentage_change_close_open = ((close_price - open_price) / open_price) * 100
            percentage_changes_close_open.append(percentage_change_close_open)

    diffs_close = pd.Series(diffs_close, index=dates[:len(diffs_close)])
    percentage_changes_close_open = pd.Series(percentage_changes_close_open, index=dates[:len(percentage_changes_close_open)])
    percentage_changes_1730_1800 = pd.Series(percentage_changes_1730_1800, index=dates[:len(percentage_changes_1730_1800)])

    # Grafik çizimi
    fig = make_subplots(rows=3, cols=1, subplot_titles=('Günlük Fiyat Farkları (Kapanış - Açılış)',
                                                        'Günlük Yüzde Fiyat Değişimleri (17:59 Kapanış - 10:00 Açılış)',
                                                        'Günlük Yüzde Fiyat Değişimleri (17:30 - 18:00)'))

    # Kapanış fiyatı farkları çizimi
    for i in range(len(diffs_close) - 1):
        x_values = [diffs_close.index[i], diffs_close.index[i + 1]]
        y_values = [diffs_close.values[i], diffs_close.values[i + 1]]

        # Renk belirleme ve çizgi segmentasyonu
        if y_values[0] >= 0 and y_values[1] >= 0:
            color = 'green'
        elif y_values[0] <= 0 and y_values[1] <= 0:
            color = 'red'
        else:
            # 0 çizgisini geçtiği noktayı bul
            intersection_x = x_values[0] + (x_values[1] - x_values[0]) * (0 - y_values[0]) / (y_values[1] - y_values[0])
            intersection_y = 0

            # 0 çizgisiyle kesişim noktasını çiz
            fig.add_trace(go.Scatter(
                x=[x_values[0], intersection_x],
                y=[y_values[0], intersection_y],
                mode='lines',
                line=dict(color='green' if y_values[0] >= 0 else 'red', width=2),
                showlegend=False
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=[intersection_x, x_values[1]],
                y=[intersection_y, y_values[1]],
                mode='lines',
                line=dict(color='green' if y_values[1] >= 0 else 'red', width=2),
                showlegend=False
            ), row=1, col=1)
            continue

        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines+markers',
            marker=dict(color=color),
            line=dict(color=color, width=2),
            showlegend=False
        ), row=1, col=1)

    # Yüzde değişim bar grafikleri
    fig.add_trace(go.Bar(
        x=percentage_changes_close_open.index,
        y=percentage_changes_close_open.values,
        name='Yüzde Değişim (17:59 - 10:00)',
        marker_color='blue'
    ), row=2, col=1)

    fig.add_trace(go.Bar(
        x=percentage_changes_1730_1800.index,
        y=percentage_changes_1730_1800.values,
        name='Yüzde Değişim (17:30 - 18:00)',
        marker_color='orange'
    ), row=3, col=1)

    fig.update_layout(
        title='Günlük Fiyat Farkları ve Yüzde Değişim',
        xaxis_title='Günler',
        yaxis_title='Fiyat Farkı',
        xaxis2_title='Günler',
        yaxis2_title='Yüzde Değişim (17:59 - 10:00)',
        xaxis3_title='Günler',
        yaxis3_title='Yüzde Değişim (17:30 - 18:00)',
        xaxis=dict(
            tickmode='array',
            tickvals=diffs_close.index,
            ticktext=[date.strftime('%Y-%m-%d') for date in diffs_close.index],
            tickangle=-45
        ),
        xaxis2=dict(
            tickmode='array',
            tickvals=percentage_changes_close_open.index,
            ticktext=[date.strftime('%Y-%m-%d') for date in percentage_changes_close_open.index],
            tickangle=-45
        ),
        xaxis3=dict(
            tickmode='array',
            tickvals=percentage_changes_1730_1800.index,
            ticktext=[date.strftime('%Y-%m-%d') for date in percentage_changes_1730_1800.index],
            tickangle=-45
        ),
        shapes=[dict(type='line', y0=0, y1=0, x0=diffs_close.index[0], x1=diffs_close.index[-1],
                     line=dict(dash='dash', color='red'))]
    )

    return fig

if __name__ == "__main__":
    input_file = 'kapanısta_al_acılısta_sat/F_XU0300624_trades_1min.txt'
    output_image = 'price_differences.html'
    analyze_data(input_file, output_image)
