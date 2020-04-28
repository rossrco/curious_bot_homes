import time
import random
import yaml
import certifi
import urllib3
from bs4 import BeautifulSoup
import requests
import json
import pandas as pd

with open('config.yaml', 'r') as config_file:
    config = yaml.load(config_file, Loader=yaml.SafeLoader)


def compose_url(area, new_ad, property_type):
    url = config['overview_page']

    url += config['lifecycle']['for_sale'] + '&'

    for a in area.split(','):
        url += config['area_codes'][a] + '&'

    url += config['property_type'][property_type] + '&'

    if new_ad is True:
        url += config['new_ad']

    return url


def extract_ad_tiles(url, min_wait, max_wait, max_pages):
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                               ca_certs=certifi.where())

    i = 1
    r_button = True

    while i <= max_pages and r_button:
        time.sleep(random.randint(min_wait, max_wait))
        page_url = url + f'&page={i}'
        page = http.request('GET', page_url)
        parsed = BeautifulSoup(page.data.decode('utf-8'), 'html.parser')
        ads = parsed.findAll('article', {'class': config['tag']['ad_unit']})
        i += 1
        r_button_tag = parsed.find('a', {'class': config['tag']['r_button']})
        r_button = r_button_tag is not None
        for a in ads:
            yield a


def extract_tile_details(ad, property_type):
    details = {}
    link_tag = ad.find('a', {'class': config['tag']['link']})
    img_tag = ad.find('div', {'class': config['tag']['img']})
    addr_tag = ad.find('div', {'class': config['tag']['addr']})
    price_area_tag = ad.find('div', {'class': config['tag']['price_area']})\
        .findAll('div')
    promo_tag = ad.find('span', {'class': config['tag']['promo']})

    details['id'] = link_tag['id']
    details['link'] = config['link_prefix'] + link_tag['href']
    details['img_link'] = img_tag.img['src']
    details['short_desc'] = link_tag.string.strip()
    details['address'] = addr_tag.string.strip()
    details['new_building'] = 'newbuildings' in details['link']
    details['main_price'] = price_area_tag[1].string.strip()
    details['viewed'] = time.strftime('%Y-%m-%d %X')
    details['size'] = price_area_tag[0].string.strip()
    details['type'] = property_type
    details['promoted'] = promo_tag is not None
    details['geocode'] = get_gmaps_geocode(details['address'])

    return details


def get_gmaps_geocode(address):
    google_maps_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'address': address,
              'key': config['gmaps_key']}

    response = requests.get(google_maps_url, params=params)
    return json.dumps(response.json())


def extract_ads(area, new_ad, property_type, verbose, min_wait, max_wait,
                max_pages):
    url = compose_url(area, new_ad, property_type)

    ad_tiles = extract_ad_tiles(url, min_wait, max_wait, max_pages)

    data = []
    for ad in ad_tiles:
        ad_details = extract_tile_details(ad, property_type)
        data.append(ad_details)

    return data


def run(area, new_ad, property_type, verbose, min_wait, max_wait, max_pages):
    run_res = []

    for p in property_type.split(','):
        run_res += extract_ads(area, new_ad, p, verbose, min_wait, max_wait,
                               max_pages)

    res_df = pd.DataFrame(run_res)
    res_df.to_csv('result.csv', index=False)


if __name__ == '__main__':
    import argparse
    parser = argparse.\
        ArgumentParser(description='Run the housing data extractor')

    parser.add_argument('--area',
                        help='Comma separated area names',
                        type=str,
                        default='oslo')
    parser.add_argument('--new_ad',
                        help='Get only new ads',
                        type=bool,
                        default=True)
    parser.add_argument('--property_type',
                        help='Comma separated property types',
                        type=str,
                        default='detached,semi_detached,apartment,terraced')
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

    run(args.area, args.new_ad, args.property_type, args.verbose,
        args.min_wait, args.max_wait, args.max_pages)
