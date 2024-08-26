import streamlit as st

# Sayfa yapılandırmasını ayarla (sadece burada olmalı)
st.set_page_config(page_title="Finansal Araçlar", page_icon="", layout="wide")

# Sayfa navigasyonu
st.sidebar.title("Navigasyon")
selected_page = st.sidebar.radio("Sayfa seçin:", [
    "Ana Sayfa",
    "Veri Görselleştirme",
    "Kapanışta Al Açılışta Sat Stratejisi",
    "Yükseliş Takip Stratejisi",
    "Bedelli Sermaye Artırımı Şirketleri",
    "Bedelsiz Sermaye Artırımı Şirketleri",
    "Türkiye'nin Tatilleri",
    "Sermaye Artırımı Şirketleri",  # Yeni eklenen sayfa
    "Yeni Sayfa",
    "Warrants",
])

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
elif selected_page == "Bedelli Sermaye Artırımı Şirketleri":
    import bedelli_sermaye_artirimi
    bedelli_sermaye_artirimi.show_page()
elif selected_page == "Bedelsiz Sermaye Artırımı Şirketleri":
    import bedelsiz_sermaye_artirimi
    bedelsiz_sermaye_artirimi.show_page()
elif selected_page == "Türkiye'nin Tatilleri":
    import tatiller
    tatiller.show_holidays_page()
elif selected_page == "Sermaye Artırımı Şirketleri":  # Yeni eklenen sayfa
    import sermaye_artirimi
    sermaye_artirimi.show_sermaye_artirimi_page()
elif selected_page == "Yeni Sayfa":
    import yeni_sayfa
    yeni_sayfa.show_page()
elif selected_page == "Warrants":
    import warrants
    warrants.show_page()
