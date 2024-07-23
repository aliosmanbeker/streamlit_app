from bs4 import BeautifulSoup
import pandas as pd
from scrape_table import get_table_data, requests_retry_session

# Hedef URL
url = 'https://www.kap.org.tr/tr/cgifAllCompaniesItem/intanceFile_oda-50000_Shareholders/InCaseThatThereAreVotingPrivilegesIndicateTheOwnerAndPercentageOfTheVotingMajorityOfShares'

# Web sayfasını getir
response = requests_retry_session().get(url)
response.raise_for_status()

# BeautifulSoup ile HTML içeriğini ayrıştır
soup = BeautifulSoup(response.text, 'html.parser')

# Tablodaki şirket isimlerini ve linkleri çek
company_links = []
table = soup.find('table')
for row in table.find_all('tr')[1:]:  # İlk satır başlık olduğu için atlanır
    cells = row.find_all('td')
    if len(cells) > 0:
        company_name = cells[0].get_text(strip=True)
        link_suffix = cells[0].find('a')['href']
        link = 'https://www.kap.org.tr' + link_suffix.replace('/ozet', '/genel')
        company_links.append((company_name, link))

# Pandas DataFrame oluştur
df = pd.DataFrame(company_links, columns=['Hisse', 'Link'])

# Diğer sütunları ekle
df['Pay Grubu'] = ''
df['İmtiyaz Türü'] = ''
df['Borsada işlem görüp görmediği'] = ''

# Her bir linki ziyaret ederek gerekli bilgileri çek
for index, row in df.iterrows():
    # print(f"Processing {row['Hisse']} at {row['Link']}")
    table_data = get_table_data(row['Link'])
    # print(table_data)
    if table_data:
        for data_row in table_data:
            # print(data_row[0])
            # print(len(data_row))
            if len(data_row) >= 3 and data_row[5] != 'İşlem Görmüyor':
                df.at[index, 'Pay Grubu'] = data_row[0]
                df.at[index, 'İmtiyaz Türü'] = data_row[4]
                df.at[index, 'Borsada işlem görüp görmediği'] = data_row[5]
                break

# Terminale yazdır
print(df)


# Alternatif olarak DataFrame'i CSV dosyasına kaydet
df.to_csv('company_data.csv', index=False)

# df = pd.read_csv('company_data.csv')
# print(df[df['Borsada işlem görüp görmediği'] == 'İşlem Görüyor'])
# filtrelenmis_data = df[df['Borsada işlem görüp görmediği'] == 'İşlem Görüyor']
# filtrelenmis_data.to_csv('filtrelenmis_data.csv', index=False)