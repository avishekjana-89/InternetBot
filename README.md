# ScrapCustomAuthorityData
Need to extract data from websites of different national customs authorities.
This first project would be a small number of files form a website in japan ( english language)

this is a first test project fixed price

pages look like this
https://www.customs.go.jp/english/tariff/2021_9/data/e_02.htm
we need the data in the table

# ScrapWikiList.py
There is a Wiki page containing a list of businesses. We need you to scrape these business names.

Each business name has their own Wiki page. We also need you to scrape the first paragraph of this.

Create a HTML file in this format containing "H2" (for the business name) and "P" (for the first praagraph of the Wiki page) HTML tags, simlar to this:

Business Name 1
The first paragraph of the buisness' Wiki page.

Business Name 2
The first paragraph of the buisness' Wiki page.

Afterwards, remove all businesses with only 2 or less sentences in the first paragraph.

You must also remove Wiki referneces (such as [1]) and links from the scrape.

# InternetBot.py
This bot extract content and data from a web table of W3Schools site and save into a csv file.

In order to run InternetBot.py file, 2 python library apis need to be downloaded.
  1. pip install selenium
  2. pip install webdriver.manager

Once downloaded, goto location where you saved InternetBot.py file in your system and open **cmd** from that path.
Then run **python InternetBot.py** from cmd.

you will see a **Export.csv** in same location once extract is completed.
