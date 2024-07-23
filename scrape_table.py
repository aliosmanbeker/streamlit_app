import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def get_table_data(url):
    response = requests_retry_session().get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    header_div = soup.find('div', class_='type-normal vcell exportTitle', string='Sermayeyi Temsil Eden Paylara İlişkin Bilgi')
    if not header_div:
        print("Başlık bulunamadı.")
        return None

    parent_div = header_div.find_parent('div', class_='column-type1 vtable alignTextToLeft overflow-all-auto')
    if not parent_div:
        print("Parent div bulunamadı.")
        return None

    table_div = parent_div.find_next_sibling('div', class_='exportDiv')
    if not table_div:
        print("Tablo içeriği bulunamadı.")
        return None

    table_class_div = table_div.find('div', class_='exportClass')
    if not table_class_div:
        print("Tablo class div bulunamadı.")
        return None

    rows = table_class_div.find_all('div', class_='w-clearfix w-inline-block a-table-row infoRow')
    if not rows:
        print("Tablo satırları bulunamadı.")
        return None

    data = []
    for row in rows:
        if 'font-weight: 600' not in row.get('style', ''):
            cells = row.find_all('div', class_='comp-cell-row-div vtable infoColumn')
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            data.append(cell_texts)
    return data

def get_stock_code(url):
    response = requests_retry_session().get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    stock_code_element = soup.find('h6')
    if not stock_code_element:
        print("Borsa kodu bulunamadı.")
        return None

    return stock_code_element.get_text(strip=True)

def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session
