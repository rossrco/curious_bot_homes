import re
import time
import datetime
import subprocess
import random
import yaml
import certifi
import urllib3
from bs4 import BeautifulSoup
import json
import googlemaps


with open('config.yaml', 'r') as config_file:
    config = yaml.load(config_file, Loader=yaml.SafeLoader)


gmaps_key = config['gmaps_key']
gmaps = googlemaps.Client(gmaps_key)
version = subprocess\
    .check_output(['git', 'describe', '--always']).decode('utf-8')


def compose_url(area, new_ad, property_type):
    url = config['overview_page']

    url += '&' + config['lifecycle']['for_sale']

    for a in area.split(','):
        url += '&' + config['area_codes'][a]

    url += '&' + config['property_type'][property_type]

    if new_ad is True:
        url += '&' + config['new_ad']

    return url


def extract_ad_tiles(url, min_wait, max_wait, max_pages):
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                               ca_certs=certifi.where())

    i = 1
    r_button = True

    while i <= max_pages and r_button:
        time.sleep(random.randint(min_wait, max_wait))
        page_url = url + f'&page={i}'
        print(page_url)
        page = http.request('GET', page_url)
        parsed = BeautifulSoup(page.data.decode('utf-8'), 'html.parser')
        ads = parsed.findAll('article', {'class': config['tag']['ad_unit']})
        print(f'Viewed {len(ads)} ads on page {i}.')
        i += 1
        r_button_tag = parsed.find('a', {'class': config['tag']['r_button']})
        r_button = r_button_tag is not None
        for a in ads:
            yield a


def extract_area_price(price_area_tag):
    area = None
    price = None
    if price_area_tag is None:
        return (area, price)
    elif len(price_area_tag) < 2:
        price = price_area_tag[0].string.strip()
        return (area, price)
    else:
        area = price_area_tag[0].find(string=re.compile('\d')).strip()
        price = price_area_tag[1].find(string=re.compile('\d')).strip()
        return (area, price)


def extract_tile_details(ad, property_type):
    details = {}
    link_tag = ad.find('a', {'class': config['tag']['link']})
    img_tag = ad.find('img')
    addr_tag = ad.find('div', {'class': config['tag']['addr']})
    price_area_tag = ad.find('div', {'class': config['tag']['price_area']})\
        .findAll('div')
    promo_tag = ad.find('span', {'class': config['tag']['promo']})
    area, price = extract_area_price(price_area_tag)

    details['id'] = link_tag['id']
    details['link'] = config['link_prefix'] + link_tag['href']
    details['img_link'] = img_tag['src']
    details['short_desc'] = link_tag.string.strip()
    details['address'] = addr_tag.string.strip()
    details['new_building'] = 'newbuildings' in details['link']
    details['promoted'] = promo_tag is not None
    details['main_price'] = price
    details['area'] = area
    details['type'] = property_type
    details['viewed'] = datetime.datetime.now()
    details['detail_seen'] = None
    details['geocode'] = get_gmaps_geocode(details['address'])
    details['version'] = version

    return details


def get_gmaps_geocode(address):
    response = gmaps.geocode(address)
    return json.dumps(response[0])


def extract_ads(area, new_ad, property_type, verbose, min_wait, max_wait,
                max_pages):
    url = compose_url(area, new_ad, property_type)
    ad_tiles = extract_ad_tiles(url, min_wait, max_wait, max_pages)

    data = []
    for ad in ad_tiles:
        ad_details = extract_tile_details(ad, property_type)
        data.append(ad_details)

    return data
