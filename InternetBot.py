from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv

URL = r'https://www.w3schools.com/html/html_tables.asp'

opt = webdriver.ChromeOptions()
opt.headless = True
opt.add_argument('--disable-infobars')
opt.add_argument('--disable-extensions')
opt.add_argument('--start-maximized')
opt.add_argument('--disable-popup-blocking')
opt.add_argument('--no-sandbox')
opt.add_argument('--disable-gpu')
opt.add_argument('--disable-dev-shm-usage')
opt.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])

driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=opt)
driver.implicitly_wait(10)

try:
    driver.get(URL)

    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//h1/span[text()='Tables']")))

    header_elements = driver.find_elements_by_xpath("//table[@id='customers']/tbody/tr/th")

    csv_data = list()

    csv_data.append(list(map(lambda element: element.text, header_elements)))

    table_rows = driver.find_elements_by_xpath("//table[@id='customers']/tbody/tr")

    for row_index in range(1, len(table_rows)):
        table_data = driver.find_elements_by_xpath("//table[@id='customers']/tbody/tr[{n}]/td".format(n=row_index + 1))
        csv_data.append(list(map(lambda element: element.text, table_data)))

    with open('Export.csv', mode='w', newline='') as file:
        csv_writer = csv.writer(file, delimiter=',')
        csv_writer.writerows(csv_data)

except (NoSuchElementException, TimeoutException):
    print('Error is occurred during scraping process!')
else:
    print('Export is completed!')
finally:
    driver.quit()
