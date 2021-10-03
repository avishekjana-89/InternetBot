import requests
import bs4

wiki_list = ['Naresh Goyal', 'Mukesh Ambani', 'Ratan Tata']

for wiki in wiki_list:
    page_source = requests.get(f'https://en.wikipedia.org/wiki/{wiki}')
    soup = bs4.BeautifulSoup(page_source.text, "lxml")
    paragraph_list = soup.select('p')
    first_paragraph = paragraph_list[1]
    decompose_sup_tags = first_paragraph.select('sup')
    for tag in decompose_sup_tags:
        tag.decompose()
    business_name = soup.select('h1')[0].getText()
    html = "<!DOCTYPE html><html> <body> <h2>{}</h2> <p>{}</p></body></html>" \
        .format(business_name, first_paragraph.text)

    if html.count('.') < 3:
        continue

    with open(f'{business_name}.html', mode='w') as file:
        file.write(html)

print('Html files creation is completed!')
