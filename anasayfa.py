import streamlit as st

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
    "Sermaye Artırımı Şirketleri",
    "Haftalık Ekonomik Takvim",
    "Warrants",
    "Yeni Sayfa",
    "Warrants Listesi",
    "Varantsız Spot Listeleri",
    "Filtrelenmiş Varant Listeleri"
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
elif selected_page == "Sermaye Artırımı Şirketleri":
    import sermaye_artirimi
    sermaye_artirimi.show_sermaye_artirimi_page()
elif selected_page == "Haftalık Ekonomik Takvim":
    import haberler
    haberler.show_haberler_page()
elif selected_page == "Warrants":
    import warrants
    warrants.show_page()
elif selected_page == "Yeni Sayfa":
    import yeni_sayfa
    yeni_sayfa.show_page()
elif selected_page == "Varantsız Spot Listeleri":
    import varantsız_spot
    varantsız_spot.show_varantsiz_spot_page()
elif selected_page == "Filtrelenmiş Varant Listeleri":
    import Filtrelenmiş_Varant_Listeleri
    Filtrelenmiş_Varant_Listeleri.show_page()
elif selected_page == "Warrants Listesi":  # Warrants Listesi sayfası
    import warrants_list
    warrants_list.show_page()  # warrants_list.py içindeki show_page fonksiyonu çalıştırılır
