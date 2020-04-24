import time
import random
import yaml
import certifi
import urllib3
from bs4 import BeautifulSoup

with open('config.yaml', 'r') as config_file:
    config = yaml.load(config_file, Loader=yaml.SafeLoader)


def compose_url(area, new_ads):
    url = config['overview_page']

    for a in area.split(','):
        url += config['area_codes'][a]

    if new_ads is True:
        url += '&' + config['new_ads']

    return url


def extract_data(area, new_ads, verbose, min_wait, max_wait, max_pages):
    url = compose_url(area, new_ads)

    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                               ca_certs=certifi.where())

    i = 1
    right_button = True

    while i <= max_pages and right_button:
        time.sleep(random.randint(min_wait, max_wait))
        page_url = url + f'&page={i}'
        page = http.request('GET', page_url)
        parsed = BeautifulSoup(page.data.decode('utf-8'), 'html.parser')
        ads = parsed.findAll('article', {'class': 'ads__unit'})
        for a in ads:
            print(a)
        i += 1


if __name__ == '__main__':
    import argparse
    parser = argparse.\
        ArgumentParser(description='Run the housing data extractor')

    parser.add_argument('--area',
                        help='Comma separated area names',
                        type=str,
                        default='oslo')
    parser.add_argument('--new_ads',
                        help='Get only new ads',
                        type=bool,
                        default=True)
    parser.add_argument('--verbose',
                        help='Log full results or run silently',
                        type=bool,
                        default=True)
    parser.add_argument('--min_wait',
                        help='Minimum wait time between ad pages',
                        type=int,
                        default=1)
    parser.add_argument('--max_wait',
                        help='Maximum wait time between ad pages',
                        type=int,
                        default=2)
    parser.add_argument('--max_pages',
                        help='Maximum number of pages to visit',
                        type=int,
                        default=1)

    args = parser.parse_args()
    extract_data(args.area, args.new_ads, args.verbose, args.min_wait,
                 args.max_wait, args.max_pages)
