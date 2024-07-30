import argparse
import requests

from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd

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

    with open(path) as fp:
        soup = BeautifulSoup(fp, 'html.parser')
        table_rows = soup.find_all('div', 'table_row')

        collection = []

        for table_row in tqdm(table_rows):
            attributes = table_row.attrs
            child = requests.get(table_row.findChild('a', 'brand').attrs['href'])
            mask_page = BeautifulSoup(child.content, 'html.parser')
            mask_identifiers = mask_page.find_all('div', 'ProductMeta')
            mask_image_url = mask_page.find_all('img')[1].attrs['src']

            style = attributes['data-style']

            mask_identifier = ''
            if mask_identifiers:
                mask_identifier = mask_identifiers[0].text.strip()

            test_source = {
                'unique_internal_model_code': mask_identifier,
                'filter_type': attributes['data-type'],
                'filtration_efficiency_percent': table_row.findChild('div', 'pfe').attrs['value'],
                'breathability_pascals': table_row.findChild('div', 'breathability').text,
                'image_url': mask_image_url,
                'style': style,
                'origin': attributes['data-origin'],
                'manufacturer': attributes['data-manufacturer'],
                'strap_type': attributes['data-strap'],
                'test_source': attributes['data-test-source'],
                'where_to_buy_url': ""
            }

            collection.append(test_source)

        pathname = f'{data_path}/armbrust-testing-dataset-2024-07-30.csv'
        print(f"Saving dataset to {pathname}...")

        pd.DataFrame(collection).to_csv(pathname, index=False)
        print(f"Saved dataset to {pathname}...")
