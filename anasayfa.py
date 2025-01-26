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
    #"Warrants",
    "Yeni Sayfa",
    #"Warrants Listesi",
    #"Varantsız Spot Listeleri",
    "Filtrelenmiş Varant Listeleri",
    "DEV-Filtrelenmiş Varant Listeleri",
    "Filtrelenmiş CallVarant Listeleri",
    "DEV-Filtrelenmiş CallVarant Listeleri",
    "Holding ve Ortakları Grafiği",
    "Filtrelenmiş Future ve Bist Hisseleri",
    "Brüt Takas Hisseleri",
    "Endeks Ağırlık"
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
# elif selected_page == "Warrants":
#     import warrants
#     warrants.show_page()
elif selected_page == "Yeni Sayfa":
    import yeni_sayfa
    yeni_sayfa.show_page()
# elif selected_page == "Varantsız Spot Listeleri":
#     import varantsız_spot
#     varantsız_spot.show_varantsiz_spot_page()
elif selected_page == "Filtrelenmiş Varant Listeleri":
    import Filtrelenmiş_Varant_Listeleri
    Filtrelenmiş_Varant_Listeleri.show_page()
elif selected_page == "DEV-Filtrelenmiş Varant Listeleri":
    import Filtrelenmiş_Varant_Listeleri_dev
    Filtrelenmiş_Varant_Listeleri_dev.show_page()
elif selected_page == "Filtrelenmiş CallVarant Listeleri":
    import Filtrelenmiş_Varant_Listeleri_CALL
    Filtrelenmiş_Varant_Listeleri_CALL.show_page()
elif selected_page == "DEV-Filtrelenmiş CallVarant Listeleri":
    import Filtrelenmiş_Varant_Listeleri_CALL_dev
    Filtrelenmiş_Varant_Listeleri_CALL_dev.show_page()
elif selected_page == "Holding ve Ortakları Grafiği":
    import filtered_graph
    filtered_graph.show_page()
elif selected_page == "Filtrelenmiş Future ve Bist Hisseleri":
    import bistspotsfuture
    bistspotsfuture.main()
elif selected_page == "Brüt Takas Hisseleri":
    import brüt_takas
    brüt_takas.show_page()
elif selected_page == "Endeks Ağırlık":
    import endeks_agirlik
    endeks_agirlik.main()
# elif selected_page == "Warrants Listesi":
#     import warrants_list
#     warrants_list.show_page()
