import csv
import os
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor

import bs4
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

URL = r'https://www.psychologytoday.com/us/treatment-rehab'
US_STATE_LIST = ['alaska', 'alabama']
HEADER = [['company_name', 'tagline', 'address_line1', 'address_line2', 'address_city',
           'address_state', 'postal_code', 'first_name', 'last_name', 'phone_number',
           'lead source detail', 'about', 'specialist', 'issues', 'mental_health',
           'sexuality', 'faith', 'age', 'communities', 'out_inpatient', 'treatment_programs',
           'types_of_therapy', 'modality', 'pay_by', 'accepted_insurance_plan',
           'qualification', 'additional_credentials', 'website_url']]

next_btn_locator = "//a[@class='btn btn-default btn-next']"
page_logo_title = "//a[@title='Psychology Today']"
data_url = "//div[@class='result-row normal-result row']"
global_lock = threading.Lock()


def remove_bullet_and_add_comma_between(string):
    string_split_list = str(string).split('\n')
    strip_list = set(map(lambda x: x.strip(), string_split_list))
    strip_list.discard('')
    return ','.join(strip_list)


def browser_setup():
    os.environ['WDM_LOG_LEVEL'] = '0'
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
    driver.implicitly_wait(60)
    return driver


def find_url(driver):
    url_elements = driver.find_elements_by_xpath(data_url)
    url_list = []
    for ele in url_elements:
        url = ele.get_attribute('data-result-url')
        url_list.append(url)

    return url_list


def collect_center_urls(driver, state):
    center_list = []
    state_url = URL + "/" + state
    driver.get(state_url)
    WebDriverWait(driver, 20).until(ec.visibility_of_element_located
                                    ((By.XPATH, page_logo_title)))
    next_btn = driver.find_elements_by_xpath(next_btn_locator)
    url_list = find_url(driver)
    center_list = center_list + url_list

    while len(next_btn) > 0:
        driver.find_element_by_xpath(next_btn_locator).click()
        WebDriverWait(driver, 20).until(ec.visibility_of_element_located
                                        ((By.XPATH, page_logo_title)))
        url_list = find_url(driver)
        center_list = center_list + url_list
        next_btn = driver.find_elements_by_xpath(next_btn_locator)

    return center_list


def create_csv_file(csv_data, mode):
    while global_lock.locked():
        time.sleep(0.01)
        continue

    global_lock.acquire()
    with open('Psychology_Data.csv', mode=mode, newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file, delimiter=',')
        csv_writer.writerows(csv_data)
    global_lock.release()


def main(state):
    driver = browser_setup()
    try:
        csv_data = []
        center_list = collect_center_urls(driver, state)
        # center_list.append('https://www.psychologytoday.com/us/treatment-rehab/alabama/420614?sid=6159d884858e6&ref=29')
        # print(center_list)
        for center in center_list:
            try:
                driver.get(center)
                WebDriverWait(driver, 20).until(ec.visibility_of_element_located
                                                ((By.XPATH, page_logo_title)))
                # print(driver.page_source)
                soup = bs4.BeautifulSoup(driver.page_source, 'lxml')
                company_profile = soup.select('#contactBarPhoto')[0]
                company_name = company_profile.select('h1')[0].text.strip()
                tag = company_profile.select('h2')[0].text.strip()
                tagline = ''.join(tag.split())

                address_line1 = address_line2 = address_city = address_state = postal_code = ''
                location_address_phone = soup.select('.location-address-phone')
                address_lines = location_address_phone[0].select('.location-wrap')

                if len(address_lines) == 2:
                    address_line1 = address_lines[0].text.strip()
                    address_line2 = address_lines[1].text.strip()
                elif len(address_lines) == 1:
                    address_line1 = address_lines[0].text.strip()
                    address_line2 = ''
                elif len(address_lines) == 0:
                    address_line1 = ''
                    address_line2 = ''

                address_lines = location_address_phone[0].select('span')
                for address in address_lines:
                    if address.get('itemprop') == 'addressLocality':
                        city = address.text.strip()
                        if city.endswith(","):
                            address_city = city[0:-1]
                        else:
                            address_city = city
                    elif address.get('itemprop') == 'addressRegion':
                        address_state = address.text.strip()
                    elif address.get('itemprop') == 'postalcode':
                        postal_code = address.text.strip()

                for element in location_address_phone:
                    name = element.select('.address-call-name')
                    if len(name) != 0:
                        call, first_name, last_name = name[0].text.split(maxsplit=2)
                        break

                phone_number = location_address_phone[0].select('a')[0].text
                about = soup.select('.profile-personalstatement-body')[0].text.strip()

                specialist = issues = mental_health = sexuality = faith = age = communities = \
                    out_inpatient = treatment_programs = types_of_therapy = modality = ''
                for ele in soup.select('.specialties-section.top-border'):
                    headers = ele.select('h5')
                    for i in range(0, len(headers)):
                        if headers[i].text == 'Specialties':
                            specialist = remove_bullet_and_add_comma_between(ele.select('ul')[i].text.strip())
                        elif headers[i].text == 'Issues':
                            issues = remove_bullet_and_add_comma_between(ele.select('ul')[i].text.strip())
                        elif headers[i].text == 'Mental Health':
                            mental_health = remove_bullet_and_add_comma_between(ele.select('ul')[i].text.strip())
                        elif headers[i].text == 'Sexuality':
                            sexuality = remove_bullet_and_add_comma_between(ele.select('ul')[i].text.strip())
                        elif headers[i].text == 'Faith':
                            faith = remove_bullet_and_add_comma_between(ele.select('ul')[i].text.strip())
                        elif headers[i].text == 'Age':
                            age = remove_bullet_and_add_comma_between(ele.select('ul')[i].text.strip())
                        elif headers[i].text == 'Communities':
                            communities = remove_bullet_and_add_comma_between(ele.select('ul')[i].text.strip())
                        elif headers[i].text == 'Treatment Programs':
                            treatment_programs = remove_bullet_and_add_comma_between(ele.select('ul')[i].text.strip())
                        elif headers[i].text == 'Out / Inpatient':
                            out_inpatient = remove_bullet_and_add_comma_between(ele.select('ul')[i].text.strip())
                        elif headers[i].text == 'Types of Therapy':
                            types_of_therapy = remove_bullet_and_add_comma_between(ele.select('ul')[i].text.strip())
                        elif headers[i].text == 'Modality':
                            modality = remove_bullet_and_add_comma_between(ele.select('ul')[i].text.strip())

                try:
                    pay_by = soup.select('.spec-subcat.attributes-payment-method')[0].text.strip()
                except IndexError:
                    pay_by = ''

                try:
                    accepted_insurance_plan = remove_bullet_and_add_comma_between(
                        soup.select('.spec-list.attributes-insurance')[0].select('ul')[0].text.strip())
                except IndexError:
                    accepted_insurance_plan = ''

                try:
                    qualification = remove_bullet_and_add_comma_between(
                        soup.select('.profile-qualifications.details-section.top-border')[0]
                            .select('ul')[0].text.strip())
                except IndexError:
                    qualification = ''

                try:
                    additional_credentials = remove_bullet_and_add_comma_between(
                        soup.select('.profile-additional-credentials.details-section.top-border')[0].select('ul')[
                            0].text.strip())
                except IndexError:
                    additional_credentials = ''

                redirect_url = website_url = ''
                for site in soup.select("a[data-event-label='website']"):
                    redirect_url = site.get('href')

                if redirect_url:
                    try:
                        driver.get(redirect_url)
                        website_url = driver.current_url
                    except WebDriverException:
                        website_url = redirect_url

                data_tuple = company_name, tagline, address_line1, address_line2, address_city, address_state, \
                             postal_code, first_name, last_name, phone_number, center, about, specialist, issues, \
                             mental_health, sexuality, faith, age, communities, out_inpatient, treatment_programs, \
                             types_of_therapy, modality, pay_by, accepted_insurance_plan, qualification, \
                             additional_credentials, website_url
                csv_data.append(list(data_tuple))
            except:
                print(f'Exception is thrown for url: {center}')
                traceback.print_exc()
                break

        print('Starting load available data into csv file..')
        create_csv_file(csv_data, mode='a')
        print('Export is completed!')

    except:
        traceback.print_exc()
    finally:
        driver.quit()


if __name__ == '__main__':
    start_time = time.perf_counter()
    create_csv_file(HEADER, mode='w')
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.map(main, US_STATE_LIST)
    end_time = time.perf_counter()
    print(f'Execution takes time {(end_time - start_time)/60}min')

