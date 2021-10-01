import csv
import requests
import bs4

page_source = requests.get("https://www.customs.go.jp/english/tariff/2021_9/data/e_02.htm")
soup = bs4.BeautifulSoup(page_source.text, 'lxml')
table_list = soup.select('.t')
left_table_data_set = table_list[2]
right_table_data_set = table_list[3]
left_table_row = left_table_data_set.select('tr')
right_table_row = right_table_data_set.select('tr')

csv_data = list()
for row in range(0, len(left_table_row)):
    left_table_data = left_table_row[row].select('td')
    l_data = list(map(lambda x: x.getText(strip=True), left_table_data))
    right_table_data = right_table_row[row].select('td')
    r_data = list(map(lambda x: x.getText(strip=True), right_table_data))
    csv_data.append(l_data + r_data)

# print(csv_data)
with open('data.csv', mode='w', newline='', encoding='utf-8') as file:
    csv_writer = csv.writer(file, delimiter=',')
    csv_writer.writerows(csv_data)

print('Export is completed!')
