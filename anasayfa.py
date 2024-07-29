import streamlit as st

# Sayfa yapılandırmasını ayarla
st.set_page_config(page_title="Warrant List", page_icon="", layout="wide")

# Sayfa navigasyonu
st.sidebar.title("Navigasyon")
selected_page = st.sidebar.radio("Sayfa seçin:", ["Ana Sayfa", "Veri Görselleştirme", "Kapanışta Al Açılışta Sat Stratejisi", "Yükseliş Takip Stratejisi", "Yeni Sayfa", "Warrants"])

if selected_page == "Ana Sayfa":
    st.title("Hoşgeldiniz")
    st.write("""
        Bu uygulama, şirket verilerini görselleştirmek için tasarlanmıştır.
        Soldaki menüyü kullanarak farklı sayfalara geçebilirsiniz.
    """)
elif selected_page == "Veri Görselleştirme":
    import veri_gorsellestirme
    veri_gorsellestirme.show_page()
elif selected_page == "Kapanışta Al Açılışta Sat Stratejisi":
    import backtest_analizi
    backtest_analizi.show_page()
elif selected_page == "Yükseliş Takip Stratejisi":
    import backtest2_analizi
    backtest2_analizi.show_page()
elif selected_page == "Yeni Sayfa":
    import yeni_sayfa
    yeni_sayfa.show_page()
elif selected_page == "Warrants":
    import warrants
    warrants.show_page()
