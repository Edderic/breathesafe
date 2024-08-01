import argparse
import requests
from selenium.common.exceptions import WebDriverException

from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
from selenium import webdriver
import time

def retry(lam, browser, options):
    try:
        return lam(browser)
    except WebDriverException as e:
        browser = webdriver.Chrome(options=options)
        return lam(browser)

def find_new_table_rows(table_rows):
    new_table_rows = []

    for table_row in table_rows:
        attributes = table_row.attrs
        if attributes['data-type'] in ['Surgical', 'Cloth']:
            continue

        pfe = float(table_row.findChild('div', 'pfe').attrs['value'])
        if pfe < 95:
            continue

        brand = table_row.findChild('a', 'brand')
        mask_identifier = brand.text.strip()

        # skip if we've already visited this row successfully
        if data[data['unique_internal_model_code'] == mask_identifier].shape[0] > 0:
            continue

        new_table_rows.append(table_row)

    return new_table_rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            prog='armbrust_scaper',
            description='Scrapes the Armbrust mask-testing data set',
            epilog='')

    parser.add_argument(
        '--data_path',
        default='/Users/eddericugaddan/code/breathesafe/data',
    )

    args = parser.parse_args()
    data_path = args.data_path
    path = f"{data_path}/mask-recommender/Comprehensive Mask Testing – Armbrust American.html"

    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    browser = webdriver.Chrome(options=options)
    pathname = f'{data_path}/armbrust-testing-dataset-2024-07-30.csv'

    # TODO: write code to get the index of the last item in the
    data = pd.read_csv(pathname)
    data['unique_internal_model_code'] = data['unique_internal_model_code'].str.strip()
    with open(path) as fp:
        soup = BeautifulSoup(fp, 'html.parser')
        table_rows = soup.find_all('div', 'table_row')

        collection = data

        new_table_rows = find_new_table_rows(table_rows)

        for table_row in tqdm(new_table_rows):

            brand = table_row.findChild('a', 'brand')
            url = brand.attrs['href']

            retry(lambda browser: browser.get(url), browser, options)
            # browser.get(url)
            time.sleep(10)
            html = retry(lambda browser: browser.page_source, browser, options)
            mask_page = BeautifulSoup(html, "html.parser")
            where_to_buy_urls = mask_page.find_all('p', id='mask-source')

            color = ''
            colors_html = mask_page.find_all('p', id='mask-color-text')
            if colors_html:
                color = colors_html[0].text

            where_to_buy_url_1 = ''
            if where_to_buy_urls and where_to_buy_urls[0].findChild('a'):
                try:
                    where_to_buy_url_1 = where_to_buy_urls[0].findChild('a').attrs['href']
                except Exception as e:
                    import pdb; pdb.set_trace()

            brand = table_row.findChild('a', 'brand')
            mask_identifier = brand.text.strip()

            mask_image_url = ''
            images_html = mask_page.find_all('img')
            if len(images_html) > 1:
                mask_image_url = images_html[1].attrs['src']

            attributes = table_row.attrs
            style = attributes['data-style']

            pfe = float(table_row.findChild('div', 'pfe').attrs['value'])

            row_data = pd.DataFrame([
                {
                    'unique_internal_model_code': mask_identifier,
                    'color': color,
                    'filter_type': attributes['data-type'],
                    'filtration_efficiency_percent': pfe,
                    'breathability_pascals': table_row.findChild('div', 'breathability').text,
                    'image_url': mask_image_url,
                    'style': style,
                    'origin': attributes['data-origin'],
                    'manufacturer': attributes['data-manufacturer'],
                    'strap_type': attributes['data-strap'],
                    'test_source': attributes['data-test-source'],
                    'where_to_buy_url': where_to_buy_url_1
                }
            ])

            collection = pd.concat([
                collection,
                row_data
            ])

            print(f"Saving dataset to {pathname}...")

            pd.DataFrame(collection).to_csv(pathname, index=False)
            print(f"Saved dataset to {pathname}...")

        browser.close()
        browser.quit()
