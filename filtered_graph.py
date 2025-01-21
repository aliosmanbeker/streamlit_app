import streamlit as st

def show_page():
    """
    Filtrelenmiş ağı Streamlit sayfasında görüntüler.
    """
    st.title("Filtrelenmiş Ağ Grafiği")

    html_file_path = "filtered_network_with_labels.html"

    try:
        # HTML dosyasını oku ve içeriği Streamlit'te görüntüle
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        st.components.v1.html(html_content, height=800, scrolling=True)

    except FileNotFoundError:
        st.error(f"{html_file_path} dosyası bulunamadı. Lütfen dosyanın varlığını kontrol edin.")
